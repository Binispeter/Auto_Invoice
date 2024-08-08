This Python script automates the process of generating invoices for specific orders. It mainly uses the Selenium module in Python. The script is used by a real life business. First, it extracts the credentials from a text file (creds.txt) containing the username and password of both the sites that are used to issue the invoice. Then, from the first website, emporiorologion.gr, it extracts the data (model name, quantity, price) of every product in a specific order that the user has already chose. After storing the data, it logs in the second site, live.livecis.gr, where it uses them to generate and store the order's invoice. This is my first Python Automation project. The process of developing it, really helped me feel more confident using python for web scraping and automation.