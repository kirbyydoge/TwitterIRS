# Gereken kütüphaneler
Flask==1.1.2

selenium==3.141.0

elasticsearch==7.14.0

requests==2.24.0

nltk==3.5

# Notlar
setup.py dosyası indexleri oluşturmaktadır.

Elasticsearch indexinden de duplicateleri eleyecek bir hashing ekledim. O nedenle indexleme süresi sunuma göre artabilir.

utils/crawlerutils.py dosyası crawleri bulundurmaktadır.

Crawler'i kullanmak için TW_USERNAME ve TW_PASSWORD environment variablelerini twitter kullanıcı ismi ve şifresi olarak ayarlamalısınız.

userinterface.py dosyası search / judge yardımcısını bulundurmaktadır. Çalıştırdıktan sonra konsolda belirtilen localhost:port'ta bulabilirsiniz.
 
