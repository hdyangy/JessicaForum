from datetime import datetime

class Utils:
    @staticmethod
    def getTime():
        TIME = str(datetime.now())[11:].split(':')
        TIME = TIME[0] + ':' + TIME[1] + ':' + TIME[2][:2]
        return str(TIME)

    @staticmethod
    def printIn(message, message2=""):
        print("%s-%s-%s %s - %s" %(datetime.now().year, datetime.now().month, datetime.now().day, Utils.getTime(), message))
		
    @staticmethod
    def parseJson(directory):
        with open(directory, "r") as f:
            return eval(f.read())
			
    @staticmethod
    def getHoursDiff(endTimeMillis):
        startTime = int(long(str(time.time())[:10]))
        startTime = datetime.fromtimestamp(float(startTime))
        endTime = datetime.fromtimestamp(float(endTimeMillis))
        result = endTime - startTime
        seconds = (result.microseconds + (result.seconds + result.days * 24 * 3600) * 10 ** 6) / float(10 ** 6)
        hours = int(int(seconds) / 3600) + 1
        return hours
		
    @staticmethod
    def parsePlayerName(playerName):
        return "*" + playerName[1:].lower().capitalize() if playerName.startswith("*") else playerName.lower().capitalize()