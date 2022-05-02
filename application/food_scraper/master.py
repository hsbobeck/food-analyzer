class urlBuilder:

    def constructURL(fruits):
        # NOTE : Indistinct may not be necessary in almost every case
        # indistinct = '&sxsrf=APq-WBuMTTuCJ6akx6ppvt6G2IZ-i3pc4w%3A1650990755702&ei=ox5oYoPFKpO-tQa7xYGACQ&ved=0ahUKEwjDopXsk7L3AhUTX80KHbtiAJAQ4dUDCA4&uact=5&oq=what+is+an+orange&gs_lcp=Cgdnd3Mtd2l6EAMyBQgAEIAEMgUIABCABDIFCAAQgAQyBQgAEIAEMgUIABCABDIFCAAQgAQyBQgAEIAEMgUIABCABDIFCAAQgAQyBQgAEIAEOgcIABBHELADOgoIABBHELADEIsDOgQIIxAnOgUIABCRAjoLCAAQgAQQsQMQgwE6BAgAEEM6CAguEIAEELEDOhEILhCABBCxAxCDARDHARCjAjoLCC4QgAQQsQMQgwE6DgguEIAEELEDEMcBEKMCOggIABCxAxCDAToUCC4QgAQQsQMQgwEQxwEQ0QMQ1AI6CwguEIAEEMcBEKMCOgoIABCxAxCDARBDOggIABCABBDJAzoFCAAQkgM6CAgAEIAEELEDSgUIPBIBM0oECEEYAEoECEYYAFCoBljaFmCnF2gDcAF4AIABb4gBlQySAQM5LjeYAQCgAQHIAQi4AQLAAQE&sclient=gws-wiz'
        
        urls = []
        storage = open('foods.txt', 'w')
        # Google search url builder
        for fruit in fruits:
            base = 'https://www.google.com/search?q=' + 'what+is+an+' + str(fruit) # + indistinct
            storage.writelines(base)
            storage.write('\n')
            urls = urls + [base]
        storage.close()
        return urls


if __name__ == '__main__':
    requests = ['hot_dog'] #'APPLE', 'BANANA', 'CHICKEN FRIED STEAK', 'PIZZA', 'CHOCOLATE CAKE'
    urlBuilder.constructURL(requests)
    import foodscraper
    print(foodscraper.vehicle(requests)['hot_dog'][0])
