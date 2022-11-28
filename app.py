import mysql.connector
from flask import Flask, redirect, render_template, request, url_for

application = Flask(__name__)

def getMysqlConnection():
    return mysql.connector.connect(
        user='root',
        host='localhost',
        port='3306',
        password='',
        database='utspw'
    )

def close_fk():
    db = getMysqlConnection()
    sqlstr = "SET GLOBAL FOREIGN_KEY_CHECKS=0;"
    cur = db.cursor()
    cur.execute(sqlstr)
    db.commit()
    db.close()

def open_fk():
    db = getMysqlConnection()
    sqlstr = "SET GLOBAL FOREIGN_KEY_CHECKS=1;"
    cur = db.cursor()
    cur.execute(sqlstr)
    db.commit()
    db.close()
    
nama_akun = ""
notif = "Masukkan username dan password anda"

# untuk halaman beranda
@application.route('/')
@application.route('/index')
def index():
    # manipulasi menu pada beranda
    dashboard_menu='hidden'
    menu_akun=nama_akun
    if nama_akun=='admin':
        dashboard_menu='enabled'
    elif nama_akun=='':
        menu_akun='Guest'
    underline = 'underline'
    # menampilkan halaman beranda
    return render_template(
        'index.html',menu_akun=menu_akun,dashboard_menu=dashboard_menu,underline=underline
    )

# untuk halaman informasi
@application.route('/informasi/<int:id>')
def informasi(id):
    # manipulasi menu
    dashboard_menu='hidden'
    menu_akun=nama_akun
    if nama_akun=='admin':
        dashboard_menu='enabled'
    elif nama_akun=='':
        menu_akun='Guest'
    underline='underline'
    # filter akses halaman informasi
    if nama_akun == "":
        notif="Maaf, untuk mengakses informasi sekolah kami, anda harus login terlebih dahulu 🙏"
        return render_template('index.html',notif=notif,menu_akun=menu_akun,dashboard_menu=dashboard_menu,underline=underline)
    else:
        db = getMysqlConnection()
        cur = db.cursor()
        if id == 0 :
            cur.execute("SELECT * from kelas")
            data_kelas = cur.fetchall()
            db.close()
            cur_id = str(data_kelas[0][0])
            cur_kelas = data_kelas[0][1]
        else :
            idStr = str(id)
            cur.execute("SELECT * from kelas where id_kelas='"+idStr+"'")
            data_kelas = cur.fetchall()
            db.close()
            cur_id = str(data_kelas[0][0])
            cur_kelas = data_kelas[0][1]
        # ambil data kelas
        db = getMysqlConnection()
        cur = db.cursor()
        cur.execute("SELECT * from kelas")
        data_kelas_all = cur.fetchall()
        db.close()
        # ambil data kelas berdasarkan id yang akan ditampilkan
        db = getMysqlConnection()
        cur = db.cursor()
        cur.execute("SELECT * FROM `siswa` WHERE `id_kelas`='"+cur_id+"'")
        data_siswa = cur.fetchall()
        db.close()
        # menampilkan halaman informasi
        return render_template(
            'informasi.html',
            nama_akun=nama_akun,
            data_siswa=data_siswa,
            data_kelas=data_kelas_all,
            cur_kelas=cur_kelas,
            menu_akun=menu_akun,
            dashboard_menu=dashboard_menu,
            underline=underline
        )

# untuk dashboard
@application.route('/dashboard')
def dashboard():
    global nama_akun 
    nama_akun= 'admin'
    # ambil data siswa
    db = getMysqlConnection()
    cur = db.cursor()
    cur.execute("SELECT * from siswa")
    data_siswa = cur.fetchall()
    db.close()
    # ambil data orang tua
    db = getMysqlConnection()
    cur = db.cursor()
    cur.execute("SELECT * from orang_tua")
    data_ortu = cur.fetchall()
    db.close()
    # ambil data guru
    db = getMysqlConnection()
    cur = db.cursor()
    cur.execute("SELECT * from guru")
    data_guru = cur.fetchall()
    db.close()
    # ambil data mapel
    db = getMysqlConnection()
    cur = db.cursor()
    cur.execute("SELECT * from mapel")
    data_mapel = cur.fetchall()
    db.close()
    # ambil data kelas
    db = getMysqlConnection()
    cur = db.cursor()
    cur.execute("SELECT * from kelas")
    data_kelas = cur.fetchall()
    db.close()
    # ambil data user
    db = getMysqlConnection()
    cur = db.cursor()
    cur.execute("SELECT * from pengguna")
    data_user = cur.fetchall()
    db.close()
    # ambil data mengajar
    db = getMysqlConnection()
    cur = db.cursor()
    cur.execute("SELECT * from mengajar")
    data_mengajar = cur.fetchall()
    db.close()
    # menampilkan halaman dashboard
    return render_template(
        'dashboard.html',
        data_siswa=data_siswa,
        data_ortu=data_ortu,
        data_guru=data_guru,
        data_mapel=data_mapel,
        data_kelas=data_kelas,
        data_user=data_user,
        data_mengajar=data_mengajar
    )

# untuk halaman login
@application.route('/login', methods=['GET', 'POST'])
def login():
    global nama_akun, notif
    print(request.method)
    if request.method == 'GET':
        # menampilkan halaman login
        return render_template(
            'login.html',notif=notif
        )
    elif request.method == 'POST':
        # ambil value form login
        nama_pengguna = request.form['username']
        kata_kunci = request.form['password']
        if (nama_pengguna != '' and kata_kunci != ''):
            # ambil data pengguna
            db = getMysqlConnection()
            curr = db.cursor()
            curr.execute("SELECT * FROM `pengguna` WHERE `nama_pengguna`='"+nama_pengguna+"'")
            data = curr.fetchone()
            # filter username dan password
            if data == None:
                notif = "Maaf Username Salah"
                return redirect('login')
            else:
                if data[1]==kata_kunci:
                    nama_akun = nama_pengguna
                    notif = "Masukkan username dan password anda"
                    return redirect('index')
                else:
                    notif = "Maaf Password Salah"
                    return redirect('login')
        else:
            return redirect('login')

# untuk sign-up / daftar akun
@application.route('/signup', methods=['GET', 'POST'])
def signup():
    notif = "Masukkan username dan password anda"
    print(request.method)
    if request.method == 'GET':
        # menampilkan halaman sign-up
        return render_template(
            'signup.html',notif=notif
        )
    elif request.method == 'POST':
        nama_pengguna = request.form['username']
        kata_kunci = request.form['password']
        kata_kunci_verif = request.form['passwordverif']
        # filter verifikasi password
        if kata_kunci != kata_kunci_verif:
            notif="Maaf password berbeda"
            return render_template(
                'signup.html',
                notif=notif
            )
        # ambil data pengguna
        db = getMysqlConnection()
        cur = db.cursor()
        cur.execute("SELECT * from pengguna")
        data_user = cur.fetchall()
        db.close()
        # filter apakah ada username yang sama?
        for item in data_user :
            print(item[0])
            if item[0] == nama_pengguna :
                notif = "✘ Maaf username telah ada"
                return render_template(
                    'signup.html',
                    notif=notif
                )
        # insert pengguna baru
        db = getMysqlConnection()
        try:
            cur = db.cursor()
            sqlstr = "INSERT INTO `pengguna` (`nama_pengguna`, `kata_kunci`) VALUES ('"+nama_pengguna+"', '"+kata_kunci+"')"
            print(sqlstr)
            cur.execute(sqlstr)
            db.commit()
            cur.close()
        except Exception as e:
            print("Error in SQL:\n", e)
        finally:
            db.close()
        # redirect ke login
        notif = "Silakan login, "+notif
        return redirect('login')

# untuk logout
@application.route('/logout')
def logout():
    global nama_akun
    nama_akun = ""
    return redirect('index')

# untuk registrasi siswa
@application.route('/registrasi', methods=['GET', 'POST'])
def registrasi():
    print(request.method)
    # ambil data orang tua
    db = getMysqlConnection()
    ambildata = "SELECT * from orang_tua ORDER BY orang_tua.kd_ortu"
    cur = db.cursor()
    cur.execute(ambildata)
    data_ortu = cur.fetchall()
    db.close()
    # membuat kode terbaru
    for item in data_ortu :
        cur_code = item[0]
    kd_ortu = cur_code+1
    # untuk membedakan registrasi by admin/user
    hidden_elemen = 'enabled'
    khusus_user = ''
    if nama_akun != 'admin':
        hidden_elemen = 'hidden'
        khusus_user = 'REGISTRASI'
    # get or post form
    if request.method == 'GET':
        # ambil data kelas
        db = getMysqlConnection()
        cur = db.cursor()
        cur.execute("SELECT * from kelas")
        data_kelas = cur.fetchall()
        db.close()
        # menampilkan halaman registrasi
        return render_template(
            'registrasi.html',
            data_kelas=data_kelas,
            kd_ortu=kd_ortu,
            hidden_elemen=hidden_elemen,
            khusus_user=khusus_user
        )
    elif request.method == 'POST':
        # ambil value form siswa
        nis = request.form['nis']
        nama = request.form['nama']
        alamat = request.form['alamat']
        tmp_lahir = request.form['tmp_lahir']
        tgl_lahir = request.form['tgl_lahir']
        gender = request.form['gender']
        agama = request.form['agama']
        id_kelas = request.form['id_kelas']
        # ambil value form orang tua
        nama_ortu = request.form['nama_ortu']
        alamat_ortu = request.form['alamat_ortu']
        telepon = request.form['telepon']
        pekerjaan = request.form['pekerjaan']
        agama_ortu = request.form['agama_ortu']
        status = request.form['status']
        # ambil data siswa
        db = getMysqlConnection()
        ambildata = "SELECT * from siswa"
        cur = db.cursor()
        cur.execute(ambildata)
        datakt = cur.fetchall()
        db.close()
        # filter value nis
        for item in datakt :
            if str(item[0]) == nis :
                sukses = "✘ Maaf nis telah ada"
                return render_template(
                    'registrasi.html',
                    sukses=sukses,
                    hidden_elemen=hidden_elemen,
                    khusus_user=khusus_user
                )
        # menonaktifkan foreign key
        close_fk()
        # insert data orang tua baru
        kdbaru = str(kd_ortu)
        db = getMysqlConnection()
        cur = db.cursor()
        sqlstr = "INSERT INTO `orang_tua` (`kd_ortu`, `nama`, `alamat`, `telp`, `pekerjaan`, `agama`, `status`) VALUES ('"+kdbaru+"', '"+nama_ortu+"' , '"+alamat_ortu+"' , '"+telepon+"', '"+pekerjaan+"', '"+agama_ortu+"', '"+status+"');"
        cur.execute(sqlstr)
        db.commit()
        cur.close()
        db.close()
        # insert data siswa baru
        db = getMysqlConnection()
        cur = db.cursor()
        sqlstr = "INSERT INTO `siswa` (`nis`, `nama`, `alamat`, `tmp_lahir`, `tgl_lahir`, `gender`, `agama`, `id_kelas`, `kd_ortu`, `tgl_daftar`) VALUES ('"+nis+"', '"+nama+"' , '"+alamat+"' , '"+tmp_lahir+"', '"+tgl_lahir+"', '"+gender+"', '"+agama+"', '"+id_kelas+"', '"+kdbaru+"', current_timestamp());"
        cur.execute(sqlstr)
        db.commit()
        cur.close()
        db.close()
        # mengaktifkan kembali foreign key
        open_fk()
        # menampilkan halaman registrasi berhasil
        sukses = "✔ Registrasi Berhasil"
        return render_template(
            'registrasi.html',
            sukses=sukses,
            hidden_elemen=hidden_elemen,
            khusus_user=khusus_user
        )     

# tambah data guru
@application.route('/addguru', methods=['GET', 'POST'])
def addguru():
    if request.method == 'GET':
        db = getMysqlConnection()
        cur = db.cursor()
        cur.execute("SELECT * from mapel")
        data_mapel = cur.fetchall()
        db.close()
        # menampilkan halaman tambah guru
        return render_template(
            'addguru.html',data_mapel=data_mapel
        )
    elif request.method == 'POST':
        # ambil value form
        nip = request.form['nip']
        nama = request.form['nama']
        alamat = request.form['alamat']
        tmp_lahir = request.form['tmp_lahir']
        tgl_lahir = request.form['tgl_lahir']
        gender = request.form['gender']
        agama = request.form['agama']
        telp = request.form['telp']
        pendidikan = request.form['pendidikan']
        status = request.form['status']
        # ambil list mengajar
        checked = request.form.getlist('mapel[]')
        print(checked)
        # mapellist = ', '.join(checked)
        # print(mapellist)
        # ambil data guru
        db = getMysqlConnection()
        cur = db.cursor()
        cur.execute("SELECT * from guru")
        data_guru = cur.fetchall()
        db.close()
        # filter nip guru apakah sudah ada?
        for item in data_guru :
            if item[0] == nip :
                sukses = "✘ Maaf NIP telah terdaftar"
                return render_template(
                    'addguru.html',
                    sukses=sukses
                )
        # close foreign key
        close_fk()
        # insert data guru baru
        db = getMysqlConnection()
        cur = db.cursor()
        sqlstr = "INSERT INTO `guru` (`nip`, `nama`, `alamat`, `tmp_lahir`, `tgl_lahir`, `gender`, `agama`, `telp`, `pendidikan`, `status`) VALUES ('"+nip+"', '"+nama+"' , '"+alamat+"' , '"+tmp_lahir+"', '"+tgl_lahir+"', '"+gender+"', '"+agama+"', '"+telp+"', '"+pendidikan+"', '"+status+"');"
        cur.execute(sqlstr)
        # insert data mengajar
        for i in checked:
            cur.execute("INSERT INTO `mengajar` (`nip`, `id_mapel`) VALUES ('"+nip+"', '"+str(i)+"')")
        db.commit()
        cur.close()
        db.close()
        # open foreign key
        open_fk()
        # menampilkan halaman tambah guru sukses
        sukses = "✔ Data berhasil diupload"
        return render_template(
            'addguru.html',
            sukses=sukses
        )     

# tambah data kelas
@application.route('/addkelas', methods=['GET', 'POST'])
def addkelas():
    print(request.method)
    # mendapatkan id kelas baru dgn menambah id terakhir
    db = getMysqlConnection()
    ambildata = "SELECT * from kelas ORDER BY kelas.id_kelas"
    cur = db.cursor()
    cur.execute(ambildata)
    data_kelas = cur.fetchall()
    db.close()
    for item in data_kelas :
        cur_code = item[0]
    id_kelas_cur = cur_code+1
    # ambil data guru
    db = getMysqlConnection()
    cur = db.cursor()
    cur.execute("SELECT * from guru")
    data_guru = cur.fetchall()
    db.close()
    # menampilkan form add new kelas
    if request.method == 'GET':
        return render_template(
            'addkelas.html',data_guru=data_guru,id_kelas_cur=id_kelas_cur
        )
    # mengambil data dan insert to database
    elif request.method == 'POST':
        # ambil data input
        id_kelas_new = str(id_kelas_cur)
        kelas = request.form['kelas']
        nip = request.form['nip']
        # insert data ke database kelas
        db = getMysqlConnection()
        cur = db.cursor()
        sqlstr = "INSERT INTO `kelas` (`id_kelas`, `kelas`, `nip`) VALUES ('"+id_kelas_new+"', '"+kelas+"' , '"+nip+"')"
        cur.execute(sqlstr)
        db.commit()
        cur.close()
        db.close()
        # menampilkan halaman tambah kelas berhasil
        sukses = "✔ Data berhasil ditambah"
        id_kelas_cur = id_kelas_cur+1
        return render_template(
            'addkelas.html',
            data_guru=data_guru,
            sukses=sukses,
            id_kelas_cur=id_kelas_cur
        )

# tambah data user
@application.route('/adduser', methods=['GET', 'POST'])
def adduser():
    print(request.method)
    # menampilkan halaman tambah user
    if request.method == 'GET':
        return render_template(
            'adduser.html'
        )
    # mengambil data dan insert to database
    elif request.method == 'POST':
        # ambil data input
        username = request.form['username']
        password = request.form['password']
        # insert data ke database pengguna
        db = getMysqlConnection()
        cur = db.cursor()
        sqlstr = "INSERT INTO `pengguna` (`nama_pengguna`, `kata_kunci`) VALUES ('"+username+"', '"+password+"')"
        cur.execute(sqlstr)
        db.commit()
        cur.close()
        db.close()
        sukses = "✔ Data berhasil ditambah"
        # menampilkan halaman tambah pengguna berhasil
        return render_template(
            'adduser.html',
            sukses=sukses
        )

# tambah data mapel
@application.route('/addmapel', methods=['GET', 'POST'])
def addmapel():
    print(request.method)
    # mendapatkan id mapel baru dgn menambah id terakhir
    db = getMysqlConnection()
    ambildata = "SELECT * from mapel ORDER BY mapel.id_mapel"
    cur = db.cursor()
    cur.execute(ambildata)
    data_kelas = cur.fetchall()
    db.close()
    for item in data_kelas :
        cur_code = item[0]
    id_mapel_cur = cur_code+1
    # menampilkan halaman tambah mapel
    if request.method == 'GET':
        return render_template(
            'addmapel.html',
            id_mapel_cur=id_mapel_cur
        )
    # mengambil data dan insert to database
    elif request.method == 'POST':
        # ambil data input
        mapel = request.form['mapel']
        # insert data ke database mapel
        db = getMysqlConnection()
        cur = db.cursor()
        sqlstr = "INSERT INTO `mapel` (`id_mapel`, `mapel`) VALUES ('"+str(id_mapel_cur)+"', '"+mapel+"')"
        cur.execute(sqlstr)
        db.commit()
        cur.close()
        db.close()
        sukses = "✔ Data berhasil ditambah"
        id_mapel_cur = id_mapel_cur + 1
        # menampilkan halaman tambah pengguna berhasil
        return render_template(
            'addmapel.html',
            id_mapel_cur=id_mapel_cur,
            sukses=sukses
        )

# untuk edit data
@application.route('/edit2/<int:key>', methods=['GET','POST'])
def edit2(key):
    # ambil data orang tua
    db = getMysqlConnection()
    cur = db.cursor()
    readData = 'SELECT * FROM orang_tua WHERE kd_ortu='+str(key)+''
    cur.execute(readData)
    data = cur.fetchone()
    # mengambil input dan update ke database
    if request.method == 'POST':
        # ambil value dari form
        kd_ortu = str(data[0])
        nama = request.form['nama']
        alamat = request.form['alamat']
        telp = request.form['telp']
        pekerjaan = request.form['pekerjaan']
        agama = request.form['agama']
        status = request.form['status']
        # update data
        sqlstr = "UPDATE `orang_tua` SET `nama`='"+nama+"', `alamat`='"+alamat+"', `telp`='"+telp+"', `pekerjaan`='"+pekerjaan+"', `agama`='"+agama+"', `status`='"+status+"' WHERE `kd_ortu`='"+kd_ortu+"'"
        cur.execute(sqlstr)
        db.commit()
        # ambil data baru
        cur.execute(readData)
        data = cur.fetchone()
        cur.close()
        db.close()
        # menampilkan halaman edit
        sukses = "✔ Data berhasil diedit"
        disabled='disabled'
        return render_template(
            'editortu.html',
            data=data,
            sukses=sukses
        )
    # menampilkan halaman edit orang tua
    else:
        cur.close()
        db.close()
        return render_template(
            'editortu.html',
            data=data
        ) 

# untuk edit data
@application.route('/edit1/<int:key>', methods=['GET','POST'])
def edit1(key):
    # ambil data siswa
    db = getMysqlConnection()
    cur = db.cursor()
    readData = 'SELECT * FROM siswa WHERE nis='+str(key)+''
    cur.execute(readData)
    data = cur.fetchone()
    # ambil dan update data
    if request.method == 'POST':
        # ambil value dari form
        nama = request.form['nama']
        alamat = request.form['alamat']
        tmp_lahir = request.form['tmp_lahir']
        tgl_lahir = request.form['tgl_lahir']
        gender = request.form['gender']
        agama = request.form['agama']
        id_kelas = request.form['id_kelas']
        # update data
        sqlstr = "UPDATE `siswa` SET `nama`='"+nama+"', `alamat`='"+alamat+"', `tmp_lahir`='"+tmp_lahir+"', `tgl_lahir`='"+tgl_lahir+"', `gender`='"+gender+"', `agama`='"+agama+"', `id_kelas`='"+id_kelas+"' WHERE `nis`='"+str(data[0])+"'"
        cur.execute(sqlstr)
        db.commit()
        # ambil data baru
        cur.execute(readData)
        data = cur.fetchone()
        cur.close()
        db.close()
        # menampilkan halaman edit siswa berhasil
        sukses = "✔ Data berhasil diedit"
        disabled='disabled'
        return render_template(
            'editsiswa.html',
            data=data,
            sukses=sukses,
            disabled=disabled
        )
    # menampilkan halaman edit siswa
    else:
        cur.close()
        db.close()
        # ambil data kelas
        db = getMysqlConnection()
        cur = db.cursor()
        cur.execute("SELECT * from kelas")
        data_kelas = cur.fetchall()
        # ambil nama kelas
        for x in data_kelas:
            if x[0]==data[7]:
                cur_id_kelas=x[1]
        db.close()
        # menampilkan edit siswa berhasil
        return render_template(
            'editsiswa.html', 
            data=data,
            data_kelas=data_kelas,
            cur_id_kelas=cur_id_kelas
        ) 

# untuk edit guru
@application.route('/edit3/<int:key>', methods=['GET','POST'])
def edit3(key):
    # ambil data mapel
    db = getMysqlConnection()
    cur = db.cursor()
    cur.execute("SELECT * from mapel")
    data_mapel = cur.fetchall()
    db.close()
    # ambil data guru dengan nip
    db = getMysqlConnection()
    cur = db.cursor()
    readData = 'SELECT * FROM guru WHERE nip='+str(key)+''
    cur.execute(readData)
    data = cur.fetchone()
    # ambil dan update 
    if request.method == 'POST':
        # ambil value dari form
        nip = str(data[0])
        nama = request.form['nama']
        alamat = request.form['alamat']
        tmp_lahir = request.form['tmp_lahir']
        tgl_lahir = request.form['tgl_lahir']
        gender = request.form['gender']
        agama = request.form['agama']
        telp = request.form['telp']
        pendidikan = request.form['pendidikan']
        status = request.form['status']
        # ambil checkboxlist
        checked = request.form.getlist('mapel[]')
        # update data
        sqlstr = "UPDATE `guru` SET `nama`='"+nama+"', `alamat`='"+alamat+"', `tmp_lahir`='"+tmp_lahir+"', `tgl_lahir`='"+tgl_lahir+"', `gender`='"+gender+"',`telp`='"+telp+"', `pendidikan`='"+pendidikan+"', `agama`='"+agama+"', `status`='"+status+"' WHERE `nip`='"+nip+"'"
        cur.execute(sqlstr)
        # delete and insert new ke database mengajar
        cur.execute("DELETE FROM `mengajar` WHERE nip="+str(key))
        for i in checked:
            cur.execute("INSERT INTO `mengajar` (`nip`, `id_mapel`) VALUES ('"+nip+"', '"+str(i)+"')")
        db.commit()
        # ambil data baru
        cur.execute(readData)
        data = cur.fetchone()
        cur.close()
        db.close()
        # menampilkan halaman edit guru berhasil
        sukses = "✔ Data berhasil diedit"
        disabled='disabled'
        return render_template(
            'editguru.html',
            data=data,
            data_mapel=data_mapel,
            sukses=sukses,
            disabled=disabled
        )
    else:
        cur.close()
        db.close()
        return render_template(
            'editguru.html',
            data=data,
            data_mapel=data_mapel
        ) 

# untuk edit kelas
@application.route('/edit4/<int:key>', methods=['GET','POST'])
def edit4(key):
    # ambil data kelas
    db = getMysqlConnection()
    cur = db.cursor()
    readData = 'SELECT * FROM kelas WHERE id_kelas='+str(key)+''
    cur.execute(readData)
    data = cur.fetchone()
    # ambil data guru
    cur = db.cursor()
    cur.execute("SELECT * from guru")
    data_guru = cur.fetchall()
    # ambil nama guru
    cur_nama_guru = 'Bambang'
    for x in data_guru:
        if x[0]==data[2]: 
            cur_nama_guru = x[1]
    # ambil dan update data
    if request.method == 'POST':
        # ambil value dari form
        id_kelas = str(data[0])
        kelas = request.form['kelas']
        nip = request.form['nip']
        # update data
        sqlstr = "UPDATE `kelas` SET `kelas`='"+kelas+"', `nip`='"+nip+"' WHERE `id_kelas`='"+id_kelas+"'"
        cur.execute(sqlstr)
        db.commit()
        # ambil data baru
        cur.execute(readData)
        data = cur.fetchone()
        cur.close()
        db.close()
        # menampilkan halaman edit kelas sukses
        sukses = "✔ Data berhasil diedit"
        disabled ='disabled'
        return render_template(
            'editkelas.html',
            data=data,
            data_guru=data_guru,
            cur_nama_guru=cur_nama_guru,
            sukses=sukses,
            disabled=disabled
        )
    # menampilkan halaman edit kelas
    else:
        cur.close()
        db.close()
        return render_template(
            'editkelas.html',
            data=data,
            data_guru=data_guru,
            cur_nama_guru=cur_nama_guru
        ) 

# untuk edit pengguna
@application.route('/edit5/<string:key>', methods=['GET','POST'])
def edit5(key):
    # ambil data pengguna
    db = getMysqlConnection()
    cur = db.cursor()
    readData = "SELECT * FROM pengguna WHERE nama_pengguna='"+key+"'"
    cur.execute(readData)
    data = cur.fetchone()
    # ambil dan update data
    if request.method == 'POST':
        # ambil value dari form
        username = request.form['username']
        password = request.form['password']
        # update data
        sqlstr = "UPDATE `pengguna` SET `nama_pengguna`='"+username+"', `kata_kunci`='"+password+"' WHERE `nama_pengguna`='"+data[0]+"'"
        cur.execute(sqlstr)
        db.commit()
        # ambil data baru
        cur.execute(readData)
        data = cur.fetchone()
        cur.close()
        db.close()
        # menampilkan halaman edit pengguna berhasil
        sukses = "✔ Data berhasil diedit"
        disabled ='disabled'
        return render_template(
            'edituser.html',
            data=data,
            sukses=sukses,
            disabled=disabled
        )
    # menampilkan halaman edit date
    else:
        cur.close()
        db.close()
        return render_template(
            'edituser.html',
            data=data
        ) 

# untuk edit mapel
@application.route('/edit6/<int:key>', methods=['GET','POST'])
def edit6(key):
    # ambil data mapel
    db = getMysqlConnection()
    cur = db.cursor()
    readData = "SELECT * FROM mapel WHERE id_mapel='"+str(key)+"'"
    cur.execute(readData)
    data = cur.fetchone()
    # ambil dan update data
    if request.method == 'POST':
        # ambil value dari form
        mapel = request.form['mapel']
        # update data
        sqlstr = "UPDATE `mapel` SET `mapel`='"+mapel+"' WHERE `id_mapel`='"+str(data[0])+"'"
        cur.execute(sqlstr)
        db.commit()
        # ambil data baru
        cur.execute(readData)
        data = cur.fetchone()
        cur.close()
        db.close()
        # menampilkan halaman edit pengguna berhasil
        sukses = "✔ Data berhasil diedit"
        disabled ='disabled'
        return render_template(
            'editmapel.html',
            data=data,
            sukses=sukses,
            disabled=disabled
        )
    # menampilkan halaman edit date
    else:
        cur.close()
        db.close()
        return render_template(
            'editmapel.html',
            data=data
        )

# untuk delete siswa dan orang tuanya
@application.route('/delete1/<int:id>')
def delete1(id):
    # ambil data siswa
    db = getMysqlConnection()
    cur = db.cursor()
    cur.execute("SELECT * from siswa ORDER BY siswa.nis")
    data_siswa = cur.fetchall()
    db.commit()
    db.close()
    # ambil kode ortu siswa
    kd_ortu = ''
    for x in data_siswa:
        if x[0] == id:
            kd_ortu = x[8]
    # delete data siswa dari nis dan orang tua dari kodenya
    db = getMysqlConnection()
    idString = str(id)
    sqlstr = "DELETE FROM siswa WHERE nis="+idString
    cur = db.cursor()
    cur.execute(sqlstr)
    sqlstr = "DELETE FROM orang_tua WHERE kd_ortu="+str(kd_ortu)
    cur = db.cursor()
    cur.execute(sqlstr)
    db.commit()
    db.close()
    # redirect ke dashboard
    return redirect('../dashboard')

# untuk delete guru
@application.route('/delete3/<int:id>')
def delete3(id):
    # menonaktifkan foreign key
    close_fk()
    # delete data guru dan mengajar dari nip
    db = getMysqlConnection()
    idString = str(id)
    cur = db.cursor()
    cur.execute("DELETE FROM guru WHERE nip="+idString)
    cur.execute("DELETE FROM mengajar WHERE nip="+idString)
    db.commit()
    db.close()
    # mengaktifkan foreign key
    open_fk()
    # redirect ke dashboard
    return redirect('../dashboard')

# untuk delete kelas
@application.route('/delete4/<int:id>')
def delete4(id):
    # delete data kelas dari id
    db = getMysqlConnection()
    idString = str(id)
    sqlstr = "DELETE FROM kelas WHERE id_kelas="+idString
    cur = db.cursor()
    cur.execute(sqlstr)
    db.commit()
    db.close()
    # redirect ke dashboard
    return redirect('../dashboard')

# untuk delete pengguna
@application.route('/delete5/<string:key>')
def delete5(key):
    # ambil data pengguna dari nama/username
    db = getMysqlConnection()
    sqlstr = "DELETE FROM pengguna WHERE nama_pengguna='"+key+"'"
    cur = db.cursor()
    cur.execute(sqlstr)
    db.commit()
    db.close()
    # redirect ke dashboard
    return redirect('../dashboard')
    
# untuk delete mapel
@application.route('/delete6/<int:key>')
def delete6(key):
    # menonaktifkan foreign key
    close_fk()
    # ambil data pengguna dari nama/username
    db = getMysqlConnection()
    cur = db.cursor()
    cur.execute("DELETE FROM mapel WHERE id_mapel='"+str(key)+"'")
    cur.execute("DELETE FROM mengajar WHERE id_mapel="+str(key))
    db.commit()
    db.close()
    # mengaktifkan foreign key
    open_fk()
    # redirect ke dashboard
    return redirect('../dashboard')

# looping
if __name__ == '__main__':
    application.run(debug=True)