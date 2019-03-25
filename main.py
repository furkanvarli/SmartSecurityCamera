
#Kütüphaneleri ekliyoruz
import time, io, picamera, cv2, numpy, smtplib, getpass, socket, datetime
from email import encoders
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText

#
mail_gonderici = "gonderici@maili.com"
mail_sifresi = "gonderici maili sifresi"
kime_gidecek = "alici@maili.com"

baslik = "Mail Konusu"
stream = io.BytesIO()

#hareket tespit algoritması
def farkImaj(t0,t1,t2):
        #girilen fotoğrafların mutlak değerle farkını alıyor
        # eğer fotoğraflar farklıysa 1 değilse 0 döndürüyor
        fark1=cv2.absdiff(t2,t1)
	fark2 = cv2.absdiff(t1, t0)
	return cv2.bitwise_and(fark1,fark2)

def hareket_tespiti():
	# fotoğrafın değişim eşiği belirlendi	
	esik_deger=200000

	#kamera bağlantısı
	kamera=cv2.VideoCapture(0)

	#kameradan alınan görüntüleri gray uzayına çevrilmesi
	t_eksi=cv2.cvtColor(kamera.read()[1],cv2.COLOR_BGR2GRAY)
	t=cv2.cvtColor(kamera.read()[1],cv2.COLOR_BGR2GRAY)
	t_arti=cv2.cvtColor(kamera.read()[1],cv2.COLOR_BGR2GRAY)
        #zaman kontrolü
	zamanKontrol=datetime.now().strftime('%Ss')
	
	while True:
		# eğer fotoğrafların farkı eşik değerinden büyükse ve
		# fotoğraflar farklı zamanlarda çekilmişse while döngüsünden çık 
                if cv2.countNonZero(farkImaj(t_eksi,t,t_arti))>esik_deger and zamanKontrol !=datetime.now().strftime('%Ss'):
			break
		zamanKontrol = datetime.now().strftime('%Ss')
		
		t_eksi=t
		t=t_arti
		t_arti=cv2.cvtColor(kamera.read()[1],cv2.COLOR_BGR2GRAY)
	#while döngüsünden çıkıldığında hareket_tespiti fonksiyonu true döndürüyor 	
	return True

# insan tespit algoritması
def vucut_tespiti():
        #kamera bağlantısı
	kamera= cv2.VideoCapture(0)
        # opencvde insan vücudu tanıma sınıflandırıcısı tanımlandı
        body_cascade = cv2.CascadeClassifier('/home/pi/opencv-3.4.0/data/haarcascades/haarcascade_fullbody.xml')
	#kamera okundu
        while True:
                
                ret, frame=kamera.read()
                #görüntü gray uzaya çevrildi
                gray=cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
                bodys=body_cascade.detectMultiScale(griton,1.3,4)

                print(str(len(bodys))+" insan tespit edildi")

                #insan vücudunun kutu içine alınması
                for (x,y,w,h) in bodys:
                        cv2.rectangle(frame,(x,y),(x+w,y+h),(0,255,255),3)

                # tespit edilen insanın görüntüsünü kaydediyor
                cv2.imwrite('tespit.jpg',frame)
                if len(bodys)>0:
                        break
        # tespit edilen insan sayısını döndürüyor
        return len(bodys)

#mail fonksiyonu
def mail():

	msg = MIMEMultipart()
        msg['From'] = mail_gonderici
        msg['To'] = kime_gidecek
        msg['Subject'] = baslik

        #mail mesajı
        msg.attach(MIMEText("Kapinizda biri tespit edildi!", 'plain'))

        # tespit edilen insan fotoğrafı ve dosya yolu tanımlanıyor
        dosya_yolu = open("tespit.jpg", "rb")
        dosya_adi = "tespit.jpg"

        part = MIMEBase('application', "octet-stream")
        part.set_payload((dosya_yolu).read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', 'attachment; filename= %s' % dosya_adi)

        msg.attach(part)

        mesaj = msg.as_string()

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.ehlo()
        server.starttls()
        server.login(mail_gonderici, mail_sifresi)
        server.sendmail(mail_gonderici, kime_gidecek, mesaj)
        print("E-mail başarıyla gönderildi")

def main():
        while True:
		if hareket_tespiti(): # eğer hareket tespit edilmişse
			if vucut_tespiti() > 0: # eğer tespit edilen insan varsa
				mail() # mail gönderilir

if __name__ == '__main__':
    main()
