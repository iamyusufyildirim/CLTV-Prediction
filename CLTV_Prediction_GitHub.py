                                                  #############################################
                                                  # BG-NBD ve Gamma-Gamma ile CLTV Prediction #
                                                  #############################################


#    ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#    +                                                            UYGULAMA ÖNCESİ                                                           +
#    ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#    +                                                                                                                                      +
#    +          Invoice StockCode                          Description  Quantity         InvoiceDate   Price  Customer ID         Country   +
#    +   0       489434     85048  15CM CHRISTMAS GLASS BALL 20 LIGHTS        12 2009-12-01 07:45:00 6.95000  13085.00000  United Kingdom   +
#    +   1       489434    79323P                   PINK CHERRY LIGHTS        12 2009-12-01 07:45:00 6.75000  13085.00000  United Kingdom   +
#    +   2       489434    79323W                  WHITE CHERRY LIGHTS        12 2009-12-01 07:45:00 6.75000  13085.00000  United Kingdom   +
#    +   3       489434     22041         RECORD FRAME 7" SINGLE SIZE         48 2009-12-01 07:45:00 2.10000  13085.00000  United Kingdom   +
#    +   4       489434     21232       STRAWBERRY CERAMIC TRINKET BOX        24 2009-12-01 07:45:00 1.25000  13085.00000  United Kingdom   +
#    +                                                                                                                                      +
#    ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


#    ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#    +                                                           UYGULAMA SONRASI                                                             +
#    ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#    +                                                                                                                                        +
#    +                Customer ID  Recency        T  Frequency  Monetary  Expected_Purc_3_Month  Expected_Average_Profit        clv Segment   +
#    +    0     12347.00000 52.14286 52.57143          7 615.71429                1.67837                631.91230 1128.44766       A         +
#    +    1     12348.00000 40.28571 51.28571          4 442.69500                1.09203                463.74596  538.80895       B         +
#    +    2     12352.00000 37.14286 42.42857          8 219.54250                2.16305                224.88677  517.50002       B         +
#    +    3     12356.00000 43.14286 46.57143          3 937.14333                1.02215                995.99892 1083.09025       A         +
#    +    4     12358.00000 21.28571 21.57143          2 575.21000                1.43879                631.90217  966.67270       A         +
#    +                                                                                                                                        +
#    ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


"""
# 1. Business Problem
# 2. Data Understanding
# 3. Data Preparation
# 4. Preparation of CLTV Prediction Data Structere
# 5. BG-NBD ile Expected Number of Transaction
# 6. Gamma-Gamma Modeli ile Expected Average Profit
# 7. BG-NBD ve Gamma-Gamma Modeli ile CLTV'nin Hesaplanması
# 8. CLTV'ye göre Segmentlerin Oluşturulması
"""


# -----------------------
# - 1. Business Problem -
# -----------------------
# Bir e-ticaret şirketi, müşterilerinin gelecekte sağlayacak olduğu faydayı tahmin etmek istemektedir.
# Bu tahminleme sonucunda benzer davranışları sergileyen müşterilerini spesifik gruplara ayırarak,
# bu gruplar özelinde farklı pazarlama yaklaşımları geliiştirerek karlılığı maksimize etme isteğini taşımaktadır.


# -------------------------
# - 2. Data Understanding -
# -------------------------
# Gerekli kütüphane, fonksiyon importları ve bazı görsel ayarlamalar
# pip install lifetimes
import pandas as pd
import matplotlib.pyplot as plt
import datetime as dt
from lifetimes import BetaGeoFitter
from lifetimes import GammaGammaFitter
from lifetimes.plotting import plot_period_transactions
pd.set_option("display.max_columns", None)
pd.set_option("display.width", 500)
pd.set_option("display.float_format", lambda x : "%.5f" % x)


# online_retail_II.xlsx veri setinin projeye dahil edilmesi
def load_dataset():
    data = pd.read_excel("data_sets/online_retail_II.xlsx", sheet_name="Year 2010-2011")
    return data

df_ = load_dataset()
df = df_.copy()


def check_df(dataframe, head=10):
    """
    Bu fonksiyonun görevi ilgili dataframe'in temel istatistiksel bilgileri
    ve yapısal özellikleri hakkında rapor oluşturmaktır.

    NOT: Bu fonksiyon, veri setinin yapısını anlamak ve olası problemleri
         belirlemek için oldukça faydalıdır.


    Parameters
    ----------
    dataframe : dataframe
                Bilgisi istenilen veri seti

    head : int
           Kaç satır gözlem birimi istenildiği bilgisi

    """
    print("###################################")
    print(f"#### İlk {head} Gözlem Birimi ####")
    print("###################################")
    print(dataframe.head(head), "\n\n")

    print("###################################")
    print("###### Veri Seti Boyut Bilgisi ####")
    print("###################################")
    print(dataframe.shape, "\n\n")

    print("###################################")
    print("######## Değişken İsimleri ########")
    print("###################################")
    print(dataframe.columns, "\n\n")

    print("###################################")
    print("####### Eksik Değer Var mı? #######")
    print("###################################")
    print(dataframe.isnull().values.any(), "\n\n")

    print("###################################")
    print("##### Betimsel İstatistikler ######")
    print("###################################")
    print(dataframe.describe().T, "\n\n")

    print("###################################")
    print("### Veri Seti Hakkında Bilgiler ###")
    print("###################################")
    print(dataframe.info())

check_df(dataframe=df)


def missing_values_table(dataframe, na_name=False):
    """
        Bu fonksiyonun görevi veri setindeki eksik değerleri
        analiz edip, ilgili değerleri tablo formatında ekrana
        bastırmaktır.

        Parameters
        ----------
        dataframe : dataframe
                    Eksik değer analizi yapılacak olan veri seti.

        na_name : bool
                  Eksik değerlere sahip değişken isimlerini
                  liste formatında ekrana bastırır.
                  NOT: Varsayılan değeri False.

        Returns
        -------
        na_name : list
                  Eksik gözlem birimine sahip olan değişken isimlerinin listesi.

        """
    na_columns = [col for col in dataframe.columns if dataframe[col].isnull().sum() > 0]
    missing_values = (dataframe[na_columns].isnull().sum()).sort_values(ascending=False)
    ratio = (dataframe[na_columns].isnull().sum() / dataframe.shape[0] * 100).sort_values(ascending=False)
    table = pd.concat([missing_values, ratio], axis=1, keys=["Value", "%"])
    print(table)

    if na_name:
        return na_columns

na_cols = missing_values_table(dataframe=df, na_name=True)


def outlier_thresholds(dataframe, variable, q1=0.25, q3=0.75):
    """
        Bu fonksiyonun görevi kendisine girilen değişkenin
        eşik değerlerini hesaplamaktır.
        Bu işlem için IQR (Interquartile Range) yöntemi kullanılır.


        Parameters
        ----------
        dataframe : dataframe
                    Uygulama yapılmak istenilen ilgili dataframe.

        variable : str
                   Uygulama yapılmak istenilen ilgili değişken.

        q1 : int, float


        q3 : int, float


        Returns
        -------
        up_limit : numpy.float64


        low_limit : numpy.float64


        """
    quartile1 = dataframe[variable].quantile(q1)
    quartile3 = dataframe[variable].quantile(q3)
    iqr = quartile3 - quartile1
    up_limit = quartile3 + 1.5 * iqr
    low_limit = quartile1 - 1.5 * iqr
    return low_limit, up_limit


def replace_with_thresholds(dataframe, variable, q1=0.25, q3=0.75):
    """
    Bu fonksiyonun görevi outlier_thresholds fonksiyonunu kullanarak
    bir değişkendeki aykırı değerleri alt ve üst limit değerleriyle
    değiştirmektir.

    Parameters
    ----------
    dataframe : dataframe
                Bilgisi istenilen veri seti

    variable : int
               Kaç satır gözlem birimi istenildiği bilgisi
    """
    low_limit, up_limit = outlier_thresholds(dataframe, variable, q1, q3)
    dataframe.loc[(dataframe[variable] < low_limit), variable] = low_limit
    dataframe.loc[(dataframe[variable] > up_limit), variable] = up_limit



# -----------------------
# - 3. Data Preparation -
# -----------------------


# Veri setindeki eksik değerleri kalıcı olarak siliyoruz.
df.dropna(inplace=True)


# İade olan işlemler veri setinin yapısını bozmktadır.
# Bu sebeple iade olan işlemleri veri setinin dışında bırakıyoruz.
df = df[~df["Invoice"].str.contains("C", na=False)]


# Quantity ve Price değişkenlerindeki minimum değer 0'dan büyük olsun isteğimizi belirtiyoruz.
df = df[df["Quantity"] > 0]
df = df[df["Price"] > 0]


# Kurulacak olan modeller istatistiksel, olasılıksal modeller olduğundan dolayı
# aykırı değerler yapılacak olan genellemelerde bazı sapmalara sebep olabilecektir.
# Bu sebepler bu değişkenlerdeki aykırı değerleri bu değişkenlerin eşik değerleriyle
# değiştirmek istediğiim bilgisini giriyorum.
replace_with_thresholds(dataframe=df, variable="Quantity", q1=0.01, q3=0.99)
replace_with_thresholds(dataframe=df, variable="Price", q1=0.01, q3=0.99)


# Bir üründen kaç adet alındığı bilgisi var, ürünün fiyat bilgisi var.
# Ancak o satın alma için ne kadar ödendiği bilgisi yok. Bir ürüne ödenen toplam değeri hesaplayalım.
df["Total_Price"] = df["Quantity"] * df["Price"]


# ----------------------------------------------------
# - 4. Preparation of CLTV Prediction Data Structere -
# ----------------------------------------------------

# BG-NBD ve Gamma-Gamma modellerinin bizden istediği bir veri formatı var. Veri setimizi BG-NBD ve Gamma-Gamma
# modellerinin bizden istediği metriklere cevap verecek bir formata çeviriyoruz.

"""
# recency: Son satın alma üzerinden geçen zaman. Haftalık. (kullanıcı özelinde),
           Müşterinin kendi içerisinde son satın alma ile ilk satın alma arasındaki farkı ifade eder.
# T: Müşterinin yaşı. Haftalık. (analiz tarihinden ne kadar süre önce ilk satın alımını yapmış)
# frequency: Tekrar eden toplam satın alma sayısı. (frequency > 1)
# monetary: satın alma başına ortalama kazanç.
"""

today_date = dt.datetime(2011, 12, 11)

cltv_prediction = df.groupby("Customer ID").agg({"InvoiceDate" : [lambda invoicedate : (invoicedate.max() - invoicedate.min()).days,
                                                                  lambda invoice : (today_date - invoice.min()).days],
                                                 "Invoice" : lambda invoice : invoice.nunique(),
                                                 "Total_Price" : lambda total_price : total_price.sum()})



# Hiyerarşik bir değişken isimlendirmesi söz konusu.
# Biz 0'ıncı seviyeyi siliyoruz.
cltv_prediction.columns = cltv_prediction.columns.droplevel(0)


cltv_prediction.columns = ["Recency", "T", "Frequency", "Monetary"]


# Recency değerini haftalık formata çevirelim
cltv_prediction["Recency"] = cltv_prediction["Recency"] / 7


# T değerini haftalık formata çevirelim
cltv_prediction["T"] = cltv_prediction["T"] / 7


# Birden fazla kez alışveriş yapan kişilere göre veri setini filtreliyoruz.
cltv_prediction = cltv_prediction[cltv_prediction["Frequency"] > 1]


# Her bir müşterinin harcama tutarını işlem sayısına bölerek
# satın alma başına ortalama kazancı hesaplamış oluruz.
cltv_prediction["Monetary"] = cltv_prediction["Monetary"] / cltv_prediction["Frequency"]




# ------------------------------------------------
# - 5. BG-NBD ile Expected Number of Transaction -
# ------------------------------------------------


# Gamma ve Beta dağılımları kullanılmıştır. Parametre bulma işlemlerinde en çok olabilirlik yöntemi kullanılmıştır.

bgf = BetaGeoFitter(penalizer_coef=0.001)

# Modeli fit ediyoruz.
bgf.fit(cltv_prediction["Frequency"],
        cltv_prediction["Recency"],
        cltv_prediction["T"])


# 1 hafta içerisinde en çok satın alma beklediğimiz 10 müşteri kimdir?

bgf.conditional_expected_number_of_purchases_up_to_time(1,
                                                        cltv_prediction["Frequency"],
                                                        cltv_prediction["Recency"],
                                                         cltv_prediction["T"]).sort_values(ascending=False)



# 3 ay içerisinde en çok satın alma beklediğimiz 10 müşteri kimdir?

bgf.conditional_expected_number_of_purchases_up_to_time(12,
                                                        cltv_prediction["Frequency"],
                                                        cltv_prediction["Recency"],
                                                        cltv_prediction["T"]).sort_values(ascending=False).head(10)


# 3 ay içerisindeki beklenen satın alma davranışlarının veri setine dahil edilmesi
cltv_prediction["Expected_Purc_3_Month"] = bgf.conditional_expected_number_of_purchases_up_to_time(12,
                                                                                                   cltv_prediction["Frequency"],
                                                                                                   cltv_prediction["Recency"],
                                                                                                   cltv_prediction["T"])


# 3 ay içerisinde toplam ne kadar satın alma olacak?
# Bu çok değerli bir çıktıdır birçok iş birimini destekleyeceek bir çıktıdır.
bgf.conditional_expected_number_of_purchases_up_to_time(12,
                                                        cltv_prediction["Frequency"],
                                                        cltv_prediction["Recency"],
                                                        cltv_prediction["T"]).sum()


# Tahmin Sonuçlarının Değerlendirilmesi
plot_period_transactions(bgf)
plt.show()


# -----------------------------------------------------
# - 6. Gamma-Gamma Modeli ile Expected Average Profit -
# -----------------------------------------------------

ggf = GammaGammaFitter(penalizer_coef=0.01)


# Modeli fit ediyoruz.
ggf.fit(cltv_prediction["Frequency"],
        cltv_prediction["Monetary"])


# Beklenen ortalama karlılıkları veri setine dahil ediyoruz.
cltv_prediction["Expected_Average_Profit"] = ggf.conditional_expected_average_profit(cltv_prediction["Frequency"],
                                                                                     cltv_prediction["Monetary"])


# -------------------------------------------------------------
# - 7. BG-NBD ve Gamma-Gamma Modeli ile CLTV'nin Hesaplanması -
# -------------------------------------------------------------

cltv_prediction_df = ggf.customer_lifetime_value(bgf,
                                                 cltv_prediction["Frequency"],
                                                 cltv_prediction["Recency"],
                                                 cltv_prediction["T"],
                                                 cltv_prediction["Monetary"],
                                                 time=3, # 3 aylık
                                                 freq="W", # T'nin frekans bilgisi
                                                 discount_rate=0.01)


cltv_prediction_df = cltv_prediction_df.reset_index()


cltv_final = cltv_prediction.merge(cltv_prediction_df, on="Customer ID", how="left")


cltv_final.sort_values(by="clv", ascending=False).head(10)


# ----------------------------------------------
# - 8. CLTV'ye göre Segmentlerin Oluşturulması -
# ----------------------------------------------

cltv_final["Segment"] = pd.qcut(cltv_final["clv"], 4, labels=["D", "C", "B", "A"])


cltv_final.sort_values(by="clv", ascending=False).head(10)


