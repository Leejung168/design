from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, ServerGroup, PasswordGroup
import json, sys, yaml
from passlib.hash import md5_crypt

import string
from random import choice
from Crypto.Cipher import XOR
import base64


# Create Database session
engine = create_engine('mysql://root:lambert@127.0.0.1:3306/cg')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


# Define ansible playbook dir
Base_Home = "/Users/lambertli/pycharm/python2/Lambert-Tool/design/new_rhel7/"

# Current Service that this platform support
support = ["Nginx", "Apache", "Mysql", "Tomcat", "Haproxy", "Java", "Redis", "PHP"]

# Define the basic Zabbix Template that will link to server
zabbix_template = ['NC_Template_Linux', 'NC_Template-Discovery_IOStat', 'NC_Template_VMstat']


# Define key
secret_key = '*XaDt(sfGd{6Qy+4q|.%0j;Fdm5?n!*~'


def encode(item):
    return item.encode("utf-8")


def encrypt(plaintext, key=secret_key):
  cipher = XOR.new(key)
  return base64.b64encode(cipher.encrypt(plaintext))


def decrypt(ciphertext, key=secret_key):
  cipher = XOR.new(key)
  return cipher.decrypt(base64.b64decode(ciphertext))


def generate_passwd(length):
    passwd_format = string.digits + string.ascii_letters
    passwd = []
    while (len(passwd) < length):
        passwd.append(choice(passwd_format))
    return ''.join(passwd)


def services_check(info):
    install = []
    for i in support:
        if i in info:
            install.append(i)
    return install


def write_pass(info,install):
    passwords = {}
    passwords["ncadmin"] = generate_passwd(12)
    passwords["root"] = generate_passwd(12)
    passwords["gpg_key"] = generate_passwd(32)

    if "Mysql" in install:
        mysql_backup = encode(info["mysql_backup"])
        passwords["mysql_root"] = generate_passwd(12)
        passwords["ncdba"] = generate_passwd(12)
        passwords["nccheckdb"] = generate_passwd(12)
        if mysql_backup == "Yes":
            passwords["ncbackupdb"] = generate_passwd(12)
        else:
            passwords["ncbackupdb"] = "-"
    else:
        passwords["mysql_root"] = "-"
        passwords["ncdba"] = "-"
        passwords["nccheckdb"] = "-"
        passwords["ncbackupdb"] = "-"
    return passwords


def generate_main_yaml(install, servername):
    main_path = Base_Home + servername + ".yml"
    roles = ['common', 'users', 'backup', 'zabbix']
    #roles = ['backup']

    for i in install:
        roles.append(i)

    temp = [{'become': True,
              'become_user': 'root',
              'hosts': 'all',
              'name': 'apply configuration to node',
              'roles': roles}]

    with open(main_path, 'w') as f:
        f.write(yaml.dump(temp))

    return main_path


def translate(srv):
    server_info = {}
    info = json.loads(srv.sservices)

    # Make sure LVM is enable or not
    try:
        CheckLVM = srv.slvm
        if CheckLVM == 'No':
            server_info["server_enable_lvm"] = False
        else:
            server_info["server_enable_lvm"] = True
            device = srv.sdisk
            server_info["vgs"] = [{'device':device, 'name':'domuvg'}]
    except:
        sys.exit("Error at Check LVM!!!")

    # Check what kind of services that this server will install
    install = services_check(info)

    # Obtain password
    passwords = write_pass(info, install)

    # Generate main yml file to run playbook
    main_path = generate_main_yaml(install, srv.sservername)


    # write password to database
    try:
        session_hostvars = DBSession()
        foreign_key = session_hostvars.query(ServerGroup).filter_by(sservername=srv.sservername).one()
        try:
            check_entry = session_hostvars.query(PasswordGroup).filter_by(sid=foreign_key.id).one()

            passwords = {'gpg_key': decrypt(check_entry.gpg_key),
                         'mysql_root': decrypt(check_entry.mysql_root),
                         'nccheckdb': decrypt(check_entry.nccheckdb),
                         'ncadmin': decrypt(check_entry.ncadmin),
                         'ncdba': decrypt(check_entry.ncdba),
                         'root': decrypt(check_entry.root),
                         'ncbackupdb': decrypt(check_entry.ncbackupdb)}
        except:
            try:
                pw = PasswordGroup(root=encrypt(passwords["mysql_root"]), ncadmin=encrypt(passwords["ncadmin"]),
                                   mysql_root=encrypt(passwords["mysql_root"]), gpg_key=encrypt(passwords["gpg_key"]),
                                   nccheckdb=encrypt(passwords["nccheckdb"]), ncbackupdb=encrypt(passwords["ncbackupdb"]),
                                   ncdba=encrypt(passwords["ncdba"]), owner=foreign_key)

                session_hostvars.add(pw)
                session_hostvars.commit()
                session_hostvars.close()
            except:
                print "Failed to write password[ncadmin, root, gpg_key] to database!!"
    except:
        pass



    for i in install:
        if i == "Nginx":
            zabbix_template.append("NC_Template_Nginx")
            server_info["nginx_version"] = encode(info["nginx_version"])
            server_info["nginx_vhosts"] = [{'bind':'0.0.0.0', 'domain':encode(info["nginx_domain"]), 'port':80}]

        if i == "Apache":
            zabbix_template.append("NC_Template_Apache")
            server_info["apache_version"] = encode(info["apache_version"])
            server_info["httpd_vhosts"] = [{'bind':'0.0.0.0', 'domain':encode(info["apache_domain"]), 'port':80}]

        if i == "Mysql":
            zabbix_template.append("NC_Template-Discovery_MySQL")
            backup = encode(info["mysql_backup"])
            server_info["mysql_root_pass"] = passwords["root"]
            server_info["mysql_nccheckdb_pass"] = passwords["nccheckdb"]
            server_info["mysql_ncdba_pass"] = passwords["ncdba"]
            if backup == "Yes":
                server_info["database_mysql_backup"] = "Yes"
                server_info["mysql_ncbackupdb_pass"] = passwords["ncbackupdb"]

        if i == "Tomcat":
            zabbix_template.append("NC_Template-Discovery_Tomcat")
            server_info["tomcat_version"] = encode(info["tomcat_version"])
            server_info["tomcat_heap_size"] = encode(info["tomcat_heapmemory"])
            server_info["java_version"] = encode(info["java_version"])

        if i == "Haproxy":
            zabbix_template.append("NC_Template-Discovery_HaProxy")
            backends = []
            haproxy_backends = encode(info["haproxy_backends"])

            for i in haproxy_backends.split(";"):
                if len(i.split()) > 0:
                    tmp = {'name':i.split()[0], 'host':i.split()[1], 'port':i.split()[2]}
                    backends.append(tmp)
                    tmp = {}

            server_info["haproxy_servers"] = backends
            server_info["haproxy_version"] = encode(info["haproxy_version"])

        if i == "Redis":
            zabbix_template.append("NC_Template-Discovery_Redis")
            server_info["redis_version"] = encode(info["redis_version"])
            server_info["redis_maxmemory"] = encode(info["redis_maxmemory"])
            server_info["maxmemory_policy"] = encode(info["redis_maxmemory_policy"])

        if i == "PHP":
            zabbix_template.append("NC_Template_PHP-FPM")
            server_info["php_version"] = encode(info["php_version"])

            #TODO: install php modules;
            server_info["php_ext"] = []
            server_info["php_pecl_ext"] = []

    # Obtain Zabbix information
    server_info["zabbix_proxy"] = encode(info["zabbix_proxy"])
    server_info["zabbix_template"] = zabbix_template
    server_info["zabbix_group"] = srv.sgroup

    # Obtain Server User
    tmp_user = encode(info["system_users"])

    users = []

    # Store customer users info
    customer_users = []
    for t in tmp_user.split(";"):
        user = t.split()
        if len(user) == 1:
            p = generate_passwd(12)
            s = {user[0]: p}
            customer_users.append(s)
            single_user = {
                "username": user[0],
                "sudo": "no",
                "password": md5_crypt.hash(p)
            }
            users.append(single_user)

        if len(user) == 2:
            p = generate_passwd(12)
            s = {user[0]: p}
            customer_users.append(s)
            if user[1] == "yes".lower():
                single_user = {
                    "username": user[0],
                    "sudo": "yes",
                    "password": md5_crypt.hash(p)
                }
                users.append(single_user)
            else:
                single_user = {
                    "username": user[0],
                    "sudo": "no",
                    "password": md5_crypt.hash(p)
                }
                users.append(single_user)

        if len(user) > 2:
            print "Wrong input at User area !!!"

    # Write customer users info into file
    with open(Base_Home + "tmp/." + srv.sservername, 'w') as f:
        f.write(json.dumps(customer_users))


    server_info["users"] = users


    # TODO AWS Backup:

    backup_dest = encode(info["backup_destination"].lower())


    server_info["gpg_key"] = passwords["gpg_key"]

    if backup_dest == "oss":
        server_info["backup_destination"] = encode(info["backup_destination"])
        server_info["aliyun_access_id"] = encode(info["backup_accessid"])
        server_info["aliyun_access_key"] = encode(info["backup_accesskey"])
        server_info["aliyun_bucket_name"] = encode(info["backup_bucketname"])
        server_info["aliyun_oss_domain"] = "oss.aliyuncs.com"

        for i in [1, 2, 3, 4]:
            backup_dir = "backup_folder"+str(i)
            if encode(info[backup_dir]) != "-":
                server_info[backup_dir] = encode(info[backup_dir])

    with open(Base_Home + "host_vars/" + srv.sservername, 'w') as f:
        f.write(yaml.dump(server_info))

    return main_path


if __name__ == '__main__':
    srv = session.query(ServerGroup).filter_by(sservername="srv-lz-rhel7").one()
    translate(srv)
