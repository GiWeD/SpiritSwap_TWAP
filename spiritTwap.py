import pandas as pd
from pycoingecko import CoinGeckoAPI
cg = CoinGeckoAPI()
import matplotlib.pyplot as plt

# the TWAP must be done over a 1week windows using 4h candles
# The DATA is retrieve from coingecko API since it's the only one free and reliable
# Candle's body:
#   1 - 2 days: 30 minutes
#   3 - 30 days: 4 hours
#   31 and before: 4 days
# The data is delivered: [UNIXTIME, OPEN, HIGH, LOW, CLOSED]


# The script will start retrieve the last 30days of information. The first information present in the csv file start from 12/12/2021.
# After read the Data it load the old information present in coingecko_spiritswap_TWAP.csv and write the new one (if a week is passed!)
# There is no need to update or whatever, just run it at least once a month please


def get_OHLC_Data(token, days ):

    token = str(token).lower() #lower the string, case sensitive
    ohlc = cg.get_coin_ohlc_by_id(token, 'usd', days)


    return ohlc

def findLastTime(tempTime, lastTime):
    for i in range(len(tempTime)):
        if(tempTime[i] >= lastTime):
            break
    return i


def main():
    TWAP_Window = 604800 #1week in seconds
    ohlcData = get_OHLC_Data('spiritswap', 30)
    dailySection  = len(ohlcData)

    #preapre lists, same kind and length, do in 1 line
    tempTimeArray = list()
    timeArray = list()
    TWAPArray = list()
    AverageSection = list()

    # retrieve and prepare data
    for i in range(dailySection):

        #retrieve the data in the list
        tempData = ohlcData[i]
        timestamp = tempData[0]
        open = tempData[1]
        high = tempData[2]
        low = tempData[3]
        close = tempData[4]

        # Average of each day’s price = (Open + High + Low + Close)/4
        AverageSection.append( (open + high + low + close) /4 )
        tempTimeArray.append ( timestamp )



    start = 0
    deltaTime = (tempTimeArray[1] - tempTimeArray[0]) /1000 # time in ms!
    pointCounter = int(TWAP_Window/deltaTime)               # cast as int remove floating zeros

    try:
        df = pd.read_csv('./csvData/coingecko_spiritswap_TWAP.csv')
        TWAPArray = list(df['twap'])
        timeArray = list(df['day'])
        lastTime = timeArray[ len(timeArray) - 1 ] #get last timestamp and start from it
        start = findLastTime(tempTimeArray, lastTime) + pointCounter
    except:
        print("Fist time fellas, got ya")
    

   
    # find TWAP over 1 week window
    for i in range(start, len(AverageSection)):
        
        if (i%pointCounter == 0):
            tempValue = 0
            for k in range(pointCounter):
                tempValue += AverageSection[i-k]
                
            TWAPArray.append(tempValue/k)
            timeArray.append(tempTimeArray[i-k]) 
        
    # zip the data
    data2 = list(zip(timeArray, TWAPArray))
    data = pd.DataFrame(data2, columns=['day','twap'])
    #pandas add always an index, name it counter
    data.index.name = 'counter'
    data.to_csv("./csvData/" + "coingecko_" +"spiritswap_TWAP.csv", sep=',', encoding='utf-8')
    

    plt.plot(TWAPArray)
    plt.xlabel('Weeks')
    plt.ylabel('Spirit Price')
    plt.show()



if __name__ == '__main__':
    main()