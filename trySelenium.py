from selenium import webdriver
import time
import re
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import os
import urllib.request
import tqdm
import random
import selenium

if __name__=="__main__":
    rootUrl="https://www.instagram.com/"
    realUrl="https://www.instagram.com/explore/locations/80388/British%20Museum/"

    userName="vincent_wwr214"
    userPwd="Wang123456#"
    totalPage=1

    driver= webdriver.Chrome('chromedriver.exe')
    driver.get(rootUrl)
    driver.find_element_by_name("username").send_keys(userName)
    driver.find_element_by_name("password").send_keys(userPwd)
    driver.find_element_by_name("password").submit()
    
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '//*[@id="react-root"]/section/main/div/div/div/section/div/button'))
    )

    driver.get(realUrl)
    
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.XPATH, '//*[@id="react-root"]/section/main/article/div[1]/div/div/div[1]/div[1]/a/div/div[2]'))
    )
    
    js='return document.body.scrollHeight;'
    height=0
    pageI=0
    while True:
        new_height = driver.execute_script(js)
        if new_height > height:
            driver.execute_script('window.scrollTo(0, document.body.scrollHeight)')
            height = new_height
            time.sleep(5)
        else:
            print("滚动条已经处于页面最下方!")
            driver.execute_script('window.scrollTo(0, 0)')#页面滚动到顶部
            break
        if pageI>=totalPage:
            break
        pageI+=1
    
    subUrlList=[]
    for subAItem in driver.find_elements_by_tag_name("a"):
        subUrlItem=subAItem.get_attribute("href")
        if len(re.findall("/p/[0-9a-zA-Z]+",subUrlItem))>0:
            subUrlList.append(subUrlItem)
    
    startI=0
    for subUrlI,subUrlItem in tqdm.tqdm(enumerate(subUrlList),desc="subpages:{}".format(len(subUrlList))):
        if subUrlI<startI:
            continue
        driver.get(subUrlItem)
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="react-root"]/section/main/div/div[1]/article/div/div[2]/div/div/div[2]'))
        )
        folderName=subUrlItem[subUrlItem.index("/p/"):].replace("/p/","").replace("/","")+"_{}".format(subUrlI)
        if folderName not in os.listdir("data"):
            os.mkdir("data/{}".format(folderName))
        
        # 评价
        commentElementList=driver.find_elements_by_tag_name("ul")[0].find_elements_by_class_name("Mr508")
        # 配文
        description=commentElementList[0].text.strip().lower().replace("\n","")
        with open("data/{}/description.txt","w+") as descriptionFile:
            descriptionFile.write(description)
        commentElementList.pop(0)
        commentList=[]
        for commentItem in commentElementList:
            commentText=commentItem.text.strip().lower().replace("\n","")
            commentList.append(commentText)
        # 点赞
        try:
            likeText=driver.find_element(By.XPATH, '//div[contains(text(),"{}")]'.format("次赞")).text
            likeNum=re.findall("[0-9]+",likeText)[0]
        except Exception as nse:
            try:
                likeText=driver.find_element(By.XPATH, '//div[contains(text(),"{}")]'.format("和")).text
                likeNum=len(likeText.replace("赞了","").split("和"))
            except:
                likeNum=0
            
            
        with open("data/{}/commentList_trans_{}_comment_{}_like_{}.txt".format(folderName,
                                                                                0,
                                                                                len(commentList),
                                                                                likeNum),"w+",encoding="utf8") as commentListFile:
            for commentTextItem in commentList:
                commentListFile.write(commentTextItem+"\n")
        # 图片存储
        imageElement=driver.find_element_by_tag_name("img")
        srcUrl=imageElement.get_attribute("src")
        imgData=urllib.request.urlopen(srcUrl).read()
        with open("data/{}/myImg.jpg".format(folderName),"wb+") as myImgFile:
            myImgFile.write(imgData)
            
        time.sleep(15+random.random()*10)

    time.sleep(3)
    driver.quit()