from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
from time import sleep
import re
from sys import exit

emp_options = Options()
#emp_options.add_argument('--headless')
#emp_options.add_argument('--disable-gpu')

#Product's Info
prod_quantities = []
prod_codes = []
prod_prices = []

creds = open('creds.txt', 'r+').readlines()
for i in range(len(creds)):
    creds[i] = creds[i].replace('\n', '')

emp_name = creds[0]
emp_passwd = creds[1]
cis_name = creds[2]
cis_passwd = creds[3]


order_input = input('Order Number: ')
driver = webdriver.Chrome(options=emp_options)
driver.get("https://www.emporiorologion.gr/admin")

driver_wait = WebDriverWait(driver, 20)

#Logging into Emporiorologion.gr
try:
    name_field = driver_wait.until(EC.presence_of_element_located((By.ID, 'login')))
    name_field.send_keys(emp_name, Keys.TAB, emp_passwd, Keys.ENTER)
    print('Login to Emporiorologion Successful. Waiting for Order to Be Found...')
except:
    print('Login Failed.')
    exit()

#Finding the Requested Order From the Site
driver_wait.until(EC.frame_to_be_available_and_switch_to_it(1))
ordini = driver_wait.until(EC.presence_of_element_located((By.ID, 'gestore_ordini'))).click()
driver.switch_to.parent_frame()
driver_wait.until(EC.frame_to_be_available_and_switch_to_it(0))
ricerca = driver.find_element(By.CLASS_NAME, 'button').click()
try:
    order_number = driver_wait.until(EC.presence_of_element_located((By.LINK_TEXT, order_input))).click()
    print('Order Found. Waiting for Data Extraction...')
except:
    print('Cannot Locate Order Number.')


try:
    #Find The Quantity Of Every Product
    temp_quantities = driver.find_elements(By.ID, 'q_inviati[]')
    for quantity in temp_quantities:
        quantity = quantity.get_attribute('value')
        prod_quantities.append(quantity)

    #Find The Code Of Every Product
    codes = driver.find_elements(By.CLASS_NAME, 'Stile3')
    for code in codes:
        prod_codes.append(code.text.split()[0])

    #Find The Price Of Every Product
    wait = WebDriverWait(driver, 0.05)
    prices_count = 0
    i = 0
    while prices_count<len(prod_codes):
        try:
            xpath = '/html/body/form/center/table[2]/tbody/tr[%d]/td[10]/font'%(i)
            temp_price = wait.until(EC.presence_of_element_located((By.XPATH, xpath)))

            temp_price = re.sub(r'[^\d,]', '', temp_price.text)

            prod_prices.append(temp_price)
            prices_count+=1
            i+=1
        except (TimeoutException, NoSuchElementException):
            i+=1

    #Calculate The Shipping Tax
    spedizione = float(driver.find_element(By.ID, 'spedizione').get_attribute('value'))
    packing_dropshiping = float(driver.find_element(By.NAME, 'packing_dropshipping').get_attribute('value'))
    handling = float(driver.find_element(By.ID, 'handling').get_attribute('value'))
    assicurazione = float(driver.find_element(By.XPATH, '(//*[@id="assicurazione"])[2]').get_attribute('value'))
    maggiorazione = float(driver.find_element(By.ID, 'maggiorazione2').get_attribute('value'))
    shipping_sum = spedizione + packing_dropshiping + handling + assicurazione + maggiorazione
    shipping_sum = str(shipping_sum)
    shipping_sum = shipping_sum.replace('.', ',')

    #Extracting Client's VAT Number 
    client_button = driver_wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/form/center/table[1]/tbody/tr[3]/td[1]/p[1]/a'))).click()
    client_afm = driver_wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="nome222"]'))).get_attribute('value')
    print('Data Extraction Successful.')
except:
    print('Data Extraction Failed. Please Try Again.')
    exit()
driver.quit()

#Logging Into live.livecis.gr and Creating New Invoice
driver = webdriver.Chrome()
driver.get('https://live.livecis.gr/live/')

driver_wait = WebDriverWait(driver, 20)

name_field = driver_wait.until(EC.element_to_be_clickable((By.ID, 'MainContent_txtunm'))).send_keys(cis_name, Keys.TAB, cis_passwd, Keys.ENTER)

moves = driver_wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="Accordion1"]/div[9]'))).click()
sales = driver_wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="ctl25_ImbtnPoliseis"]'))).click()
plus_button = driver_wait.until(EC.element_to_be_clickable((By.ID, 'MainContent_Button1'))).click()

type_tda = driver_wait.until(EC.presence_of_element_located((By.ID, "MainContent_TabContainer1_TabPanel1_DocType"))).send_keys('ΤΔΑ', Keys.ENTER)
driver_wait.until(EC.presence_of_element_located((By.ID, 'MainContent_TabContainer1_TabPanel1_Button6'))).click()
enter_afm = driver_wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="MainContent_txtFilter"]')))
enter_afm.click()
enter_afm.send_keys(client_afm)

client_found_button = enter_afm = driver_wait.until(EC.element_to_be_clickable((By.XPATH, '//tr[td[text()="%s"]]'%(client_afm)))).click()
sleep(2)

#Entering Every Product's Info
i=0
print("Entering Every Product's Info...")
while i<len(prod_codes):
    if prod_quantities[i] == '0':
        i+=1
    
    item_button = driver_wait.until(EC.element_to_be_clickable((By.ID, 'MainContent_Button2'))).click()

    arrow_button = driver_wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="MainContent_LLinkid_B-1Img"]'))).click()
    sleep(0.5)
    code_submit = driver_wait.until(EC.presence_of_element_located((By.ID, 'MainContent_LLinkid_I')))
    code_submit.clear()
    code_submit.send_keys(prod_codes[i])

    sleep(2.5)
    code_submit.send_keys(Keys.ARROW_DOWN)
    code_submit.send_keys(Keys.TAB)
    sleep(2)

    price_submit = driver_wait.until(EC.presence_of_element_located((By.ID, 'igtxtMainContent_Lprice')))
    prev_price = price_submit.get_attribute('value')
    if prev_price != prod_prices[i]:
        price_submit.clear()
        price_submit.send_keys(prod_prices[i])
        sleep(1)
        price_submit.send_keys(Keys.TAB)
    try:
        quantity_submit = driver_wait.until(EC.presence_of_element_located((By.ID, 'igtxtMainContent_Lquant')))
        quantity_submit.clear()
        quantity_submit.send_keys(prod_quantities[i])
        sleep(1)
        quantity_submit.send_keys(Keys.ENTER)
    except:
        quantity_submit = driver_wait.until(EC.presence_of_element_located((By.ID, 'igtxtMainContent_Lquant')))
        quantity_submit.clear()
        quantity_submit.send_keys(prod_quantities[i])
        sleep(1)
        quantity_submit.send_keys(Keys.TAB)

    sleep(2)
    plus_button = driver_wait.until(EC.presence_of_element_located((By.ID, 'MainContent_ImageButton1'))).click()
    i+=1
    sleep(3)
print('Products Have Been Entered Successfully.')

#Entering Shipping Tax
service_button = driver_wait.until(EC.element_to_be_clickable((By.ID, 'MainContent_BtnServ'))).click()
sleep(0.5)
driver_wait.until(EC.element_to_be_clickable((By.ID, 'MainContent_LLinkid0_B-1Img'))).click()

tax_code = driver_wait.until(EC.element_to_be_clickable((By.ID, 'MainContent_LLinkid0_I')))
tax_code.clear()
tax_code.send_keys('ΕΞΑΠΟΣΤΟΛΗΣ')
sleep(0.5)
tax_code.send_keys(Keys.TAB)
sleep(0.5)
tax_price = driver_wait.until(EC.element_to_be_clickable((By.ID, 'igtxtMainContent_Lprice0')))
tax_price.clear()
tax_price.send_keys(shipping_sum)
sleep(0.5)
tax_price.send_keys(Keys.TAB)
sleep(1)
plus_button = driver_wait.until(EC.element_to_be_clickable((By.ID, 'MainContent_ImageButton2'))).click()

sleep(5)
driver_wait.until(EC.element_to_be_clickable((By.ID, 'MainContent_Button5'))).click()


sleep(1000)
driver.quit()