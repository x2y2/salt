# _*_ coding: utf-8 _*_
"""
Created on 16/3/16
@author: liusonghui

"""
import salt
import salt.utils
import os
import subprocess
import shlex
import logging
import ftplib
from hashlib import md5
import tempfile
from glob import glob
import shutil

__virtualname__ = 'release'


def __virtual__():
    """
    :return: 返回在salt中执行时名字，为空时以文件名
    """
    return __virtualname__


REPO_PATH = tempfile.mktemp(prefix='git_release_', dir='/tmp')
VERSION_FILE = 'src/main/resources/ywapp.properties'

AppName = 'project'
AppVersion = 'project.version'
PackageName = 'project.build.finalName'
PackageSuffix = 'project.packaging'

FTP_HOST = '172.17.192.32'
FTP_PORT = 21
FTP_USER = 'night'
FTP_PASS = 'asd!23'

console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)


class PackageError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


def __ftp(ftp_host):
    ftp = ftplib.FTP()
    ftp.connect(ftp_host, FTP_PORT)
    ftp.login(FTP_USER, FTP_PASS)
    return ftp


def _clean(path):
    """
    清理克隆目录
    :return: None
    """
    subprocess.Popen(['rm', '-rf', path]).communicate()


def __get_path(release_id):
    """
    根据release_id查找代码的目录
    :param release_id: 发布id
    :return: 克隆代码所在的目录
    """
    paths = glob('/tmp/git_release_*')
    for fpath in paths:
        m = md5()
        m.update(fpath)
        dir_md5 = m.hexdigest()
        if dir_md5 == release_id:
            return fpath


def clone_code(git_url, gitcommit, runas='tomcat'):
    """
    克隆需要打包的代码
    :param git_url: 克隆代码的url
    :param gitcommit: 需要打包的分支，commitid 或是 tag
    :param runas: 拥用克隆权限的用户
    :return: [] 该次发布的id和克隆时产生的信息
    """
    ret = []
    m = md5()
    m.update(REPO_PATH)
    ret.append(m.hexdigest())
    try:
        if os.path.isdir(REPO_PATH):
            _clean(REPO_PATH)
        # 创建tomcat用户的临时目录
        command = 'su - {0} -c "mkdir {1}"'.format(runas, REPO_PATH)
        subprocess.Popen(shlex.split(command)).communicate()
        # 在临时目录中克隆
        clone_cmd = 'su - {0} -c "git clone {1} {2}"'.format(runas, git_url, REPO_PATH)
        (out_put, err_put) = subprocess.Popen(shlex.split(clone_cmd), stdout=subprocess.PIPE,
                                              stderr=subprocess.STDOUT).communicate()
        ret.append(out_put)
        # check out 出分支
        clone_cmd = 'su {0} -c "git checkout {1}"'.format(runas, gitcommit)
        (out_put, err_put) = subprocess.Popen(shlex.split(clone_cmd), cwd=REPO_PATH,
                                              stdout=subprocess.PIPE,
                                              stderr=subprocess.STDOUT).communicate()

        ret.append(out_put)
    except Exception, clone_e:
        ret.append(clone_e)
    return ret


def get_info(release_id):
    """
    获取打包前的版本，应用名称，发布版本
    :param release_id: 此次发布的id
    :return: {} 应用的名称，版本，包的名字
    """
    package_info = {}
    clone_path = __get_path(release_id)
    version_file = os.path.join(clone_path, VERSION_FILE)
    with open(version_file, 'r') as f:
        for line in f.readlines():
            package_info[line.split('=')[0].strip()] = line.split('=')[1].strip()
    suffix = package_info.get(PackageSuffix)
    package_name = map(lambda a: a + '.' + suffix, package_info.get(PackageName).split())
    package_info[PackageName] = package_name
    package_info.pop(PackageSuffix)
    return package_info


def packed(release_id, args, runas='tomcat'):
    """
    打包主程序，主要用来完成打包的动作
    :param release_id: 发布的id
    :param args: 主要的参数用来接收打包需要的命令，mvn后边的
    :param runas: 拥有打包权限的用户
    :return: str 打包过程中产生的信息
    """
    # 拼接打包命令
    make_cmd = args
    clone_path = __get_path(release_id)
    cmd_auto = 'su - {0} -c "cd {1} && mvn {2}"'.format(runas, clone_path, make_cmd)
    ret = []
    try:
        # 开始打包
        (out, err) = subprocess.Popen(shlex.split(cmd_auto),
                                      cwd=clone_path, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).communicate()
        ret.append(out)
    except Exception, packed_e:
        ret.append('make package error: {0}'.format(str(packed_e)))
    return '\n'.join(ret)


def __find_package(path, package_name):
    """
    递归搜索文件
    :param path: 搜索的目录
    :param package_name: 搜索的文件名
    :return: [] 搜索到的文件的路径
    """
    filelist = []

    for root, subFolders, files in os.walk(path):
        if 'done' in subFolders:
            subFolders.remove('done')

        for f in files:
            if f == package_name:
                filelist.append(os.path.join(root, f))

    return filelist


def __create_md5_file(fpath):
    """
    生成md5校验文件
    :param fpath: 需要生成md5校验的文件
    :return: None
    """
    m = md5()
    a_file = open(fpath, 'rb')
    m.update(a_file.read())
    a_file.close()
    fname = os.path.basename(fpath)
    fpath_md5 = "{0}.md5".format(fpath)
    fout = open(fpath_md5, 'w')
    fout.write("{0}  {1}\n".format(m.hexdigest(), fname.strip()))
    fout.flush()
    fout.close()


def upload(release_id):
    """
    上传打好包的文件到ftp服务器
    :param release_id: 发布的id
    :return: 'ok'
    """
    # 获取包的信息
    ret = []
    info = get_info(release_id)
    release_path = __get_path(release_id)
    appname = info.get(AppName)
    appversion = info.get(AppVersion)
    package_name = info.get(PackageName)
    package_path = []
    for name in package_name:
        package_path += __find_package(release_path, name)
    # 生成ftp路径
    m = md5()
    m.update(appname)
    suffix = m.hexdigest()[-4:]
    ftpdir = appname + r'-' + suffix

    bufsize = 1024
    for ftp_host in FTP_HOST.split():
            # 进入到上传app对应的目录
        upload_ftp = __ftp(ftp_host)
        try:
            remote_path = '/production/{0}/{1}'.format(ftpdir, appversion)
            for key in range(1, len(remote_path.split('/'))):
                try:
                    upload_ftp.cwd(remote_path.split('/')[key])
                except ftplib.error_perm:
                    upload_ftp.mkd(remote_path.split('/')[key])
                    upload_ftp.cwd(remote_path.split('/')[key])
            # 开如上传
            for fpath in package_path:
                __create_md5_file(fpath)
                file_handler = open(fpath, 'rb')
                upload_ftp.storbinary('STOR %s' % os.path.basename(fpath), file_handler, bufsize)
                file_handler.close()
                ret.append('{0}: {1} OK'.format(ftp_host, os.path.basename(fpath)))
                md5file = fpath + r'.md5'
                md5file_handler = open(md5file, 'rb')
                upload_ftp.storbinary('STOR %s' % os.path.basename(md5file), md5file_handler, bufsize)
                md5file_handler.close()
                ret.append('{0}: {1} OK'.format(ftp_host, os.path.basename(md5file)))
            _clean(release_path)
        except Exception, ftp_err:
            ret.append('Ftp upload error %s' % ftp_err)
        finally:
            upload_ftp.quit()
    return '\n'.join(ret)


def __download(apppath, appname, appversion, packagename):
    """
    从ftp服务器上下载指定应用版本的文件
    :param apppath: 本地存放包文件的地址
    :param appname: 需要下载的应用名
    :param appversion: 下载的包的版本
    :param packagename: 包的名字
    :return: 下载结果
    """
    m = md5()
    m.update(appname)
    suffix = m.hexdigest()[-4:]
    ftpdir = '{0}-{1}'.format(appname, suffix)
    remote_path = '/production/{0}/{1}'.format(ftpdir, appversion)
    ftp = __ftp(FTP_HOST.split()[0])
    try:
        ftp.cwd(remote_path)
    except Exception, ftp_path_error:
        return ftp_path_error
    bufsize = 1024
    localdir = apppath
    ret = []
    try:
        localpath = os.path.join(localdir, packagename + '.war')
        file_handler = open(localpath, 'wb')
        ftp.retrbinary('RETR {0}'.format(os.path.basename(localpath)), file_handler.write, bufsize)
        file_handler.close()
        local_md5 = localpath + '.md5'
        file_handler = open(local_md5, 'wb')
        ftp.retrbinary('RETR {0}'.format(os.path.basename(local_md5)), file_handler.write, bufsize)
        file_handler.close()
        p = subprocess.Popen(['md5sum', '-c', local_md5],
                             cwd=localdir, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        (out, err) = p.communicate()
        if out.split(':')[1].strip().upper() != 'OK':
            raise PackageError
        ret.append(out)
        return ret
    except Exception, ftp_down_err:
        return ftp_down_err

APP_PATH = '/tools/apps'
APP_BACKPATH = '/data/appbak'


def __backup(appname, appversion):
    """
    对当前正在运行（发布新版本前的版本）进行备份
    :param appname: 执行发布的应用名
    :param appversion: 执行发布的版本
    :return: 备份结果
    """
    app_path = os.path.join(APP_PATH, appname)
    app_backpath = os.path.join(APP_BACKPATH, '{0}/{1}-ago'.format(appname, appversion))

    if not os.path.exists(app_path):
        return '{0} not found.'.format(appname)

    if os.path.exists(app_backpath):
        p = subprocess.Popen(['rm', '-rf', app_backpath],
                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        p.communicate()
    os.makedirs(app_backpath)
    os.system('chown -R bestpay.bestpay {0}'.format(app_backpath.split('/')[1]))

    try:
        shutil.copytree(app_path, os.path.join(app_backpath, appname))
        os.system('chown -R bestpay.bestpay {0}'.format(app_backpath))
        return '{0} backup success'.format(appname)
    except Exception:
        raise IOError


def deploy(appname, appversion, packagename):
    """
    发布上线新的版本，对发布前的版本进行备份，标注为ago方便回滚操作，
    :param appname: 执行发布的应用名
    :param appversion: 执行发布的版本
    :param packagename: 执行发布的包的名字
    :return: 发布结果
    """
    ret = []
    app_path = os.path.join(APP_PATH, appname)
    if os.path.exists(app_path):
        try:
            ret.append(__backup(appname, appversion))
        except IOError:
            return '{0} backup failed'.format(appname)
        p = subprocess.Popen(['rm', '-rf', '{0}'.format(app_path)],
                             stderr=subprocess.STDOUT, stdout=subprocess.PIPE)
        (out, err) = p.communicate()
        ret.append(out)

    os.makedirs(app_path)
    os.chdir(app_path)
    try:
        ret += __download(app_path, appname, appversion, packagename)
        p = subprocess.Popen(['unzip', packagename + '.war'],
                             cwd=app_path, stderr=subprocess.STDOUT, stdout=subprocess.PIPE)
        (out, err) = p.communicate()
        ret.append(out)
        p = subprocess.Popen(['rm', '-f', packagename + '.war'],
                             cwd=app_path, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        (out, err) = p.communicate()
        ret.append(out)
        p = subprocess.Popen(['rm', '-f', packagename + '.war.md5'],
                             cwd=app_path, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        (out, err) = p.communicate()
        ret.append(out)
        p = subprocess.Popen(['chown', '-R', 'bestpay.bestpay', app_path],
                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        (out, err) = p.communicate()
        ret.append(out)
        ret.append('{0} deploy success'.format(packagename))
    except PackageError, p_e:
        return '{0} deploy failed: package broken, {1}'.format(packagename, p_e)
    except Exception, cmd_err:
        ret.append(cmd_err)
        ret.append('{0} deploy failed'.format(packagename))

    return ret


def rollback(appname, appversion):
    """
    对发布的版本立即进行回滚操作
    :param appname: 执行回滚的应用名称
    :param appversion: 执行回滚动作（当前运行）的版本号。例如: salt 172.17.162.230 release.rollback test 0.0.1 这个表示test
    应用回滚到 0.0.1 之前的一个版本，不需要记录之前的版本号是什么
    :return: 回滚结果
    """
    app_path = os.path.join(APP_PATH, appname)
    app_backpath = os.path.join(APP_BACKPATH, '{0}/{1}-ago/{0}'.format(appname, appversion))
    if not os.path.exists(app_backpath):
        return '{0} before version {1} no backup'.format(appname, appversion)
    try:
        p = subprocess.Popen(['rm', '-rf', app_path], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        p.communicate()
        shutil.copytree(app_backpath, app_path)
        p = subprocess.Popen(['chown', '-R', 'bestpay.bestpay', app_path],
                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        p.communicate()
        ret = '{0} rollback success'.format(appname)
    except Exception, rollback_err:
        ret = '{0} rollback failed: {1}'.format(appname, rollback_err)

    return ret


if __name__ == '__main__':
    pass

