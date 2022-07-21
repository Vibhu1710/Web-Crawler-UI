from flask import Flask, render_template, url_for, request, jsonify, Response
import webbrowser
import crawler
import database.LocalDataBaseMonitor as ldb
from flask_cors import cross_origin
import beforeRender
import logging
from database.ExtractedDataMonitor import removeScrapedFile


webbrowser.open('http://localhost:5000/', new=0, autoraise=True)
app = Flask(__name__)


@app.route('/')
@app.route('/home')
def home():
    return render_template("index.html", renderMap=beforeRender.getRenderMap())


@app.route('/update/<websiteId>',methods=['GET'])
def getUpdate(websiteId):
    logData = ldb.fetchWhenChange(websiteId)
    print(logData)
    response = jsonify({'State': logData[0], 'City': logData[1], 'Pin': logData[2], 'Increment': logData[3], 'Condition': logData[4]})
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response


@app.route('/rerender/<websiteId>',methods=['GET'])
def reRenderRow(websiteId):
    #  to-do
    ldb.reportOnCompletion(websiteId)

    try:
        removeScrapedFile(websiteId)
    except:
        print('could not find the file '+websiteId+'.csv in extracted_data_default_directory')

    logData = ldb.getWebsiteData(websiteId)[0]
    response = jsonify({'LastRun': logData[6], 'RowCount': logData[5]})
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response


@app.route('/run/<websiteId>',methods=['GET','POST'])
@cross_origin()
def runScript(websiteId):
    ldb.cleanLocalDataOnStart(websiteId)
    print(websiteId)
    print("before crawler")
    try:
        crawler.scrape(websiteId)
        ldb.reportOnCompletion(websiteId)
    except Exception as e:
        print(str(e))
        logging.exception("message")
        ldb.reportOnError(websiteId)
        return jsonify({'Condition': -1})

    print('after crawler')
    return jsonify({'Condition': 1})


@app.route('/continue/<websiteId>',methods=['GET','POST'])
@cross_origin()
def continueScript(websiteId):
    ldb.cleanLocalDataOnStart(websiteId)
    print(websiteId)
    print("before crawler")
    skip = int(request.json['skip'])

    try:
        crawler.scrape(websiteId,skip)
        ldb.reportOnCompletion(websiteId)
    except Exception as e:
        print(str(e))
        logging.exception("message")
        ldb.reportOnError(websiteId)
        return jsonify({'Condition': -1})

    print('after crawler')
    return jsonify({'Condition': 1})



if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
