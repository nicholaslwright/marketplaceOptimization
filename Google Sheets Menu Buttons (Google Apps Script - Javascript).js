function onOpen() {
    var ui = SpreadsheetApp.getUi();
    // Or DocumentApp or FormApp.
    ui.createMenu('Optimization')
        .addItem('Assign Orders', 'menuItem1')
        //.addItem('Assign with hard vendor constraint', 'menuItem1a'))
        .addSeparator()
        .addSubMenu(ui.createMenu('Analyze')
         .addItem('Summary', 'summarizeMeals')
         .addItem('Update Tiers in Manual Summary', 'showSummarize')
    .addItem('Fast Calc', 'calcSummarize'))
    
            //.addItem('Update COGS', 'menuItem3'))
            
    
        .addToUi();
  }
  //Send HTTP Request to AWS Lambda Function to trigger Optimization Algorithm
  function menuItem1() {
    var options = {'muteHttpExceptions' : true};
    var ss = SpreadsheetApp.getActiveSpreadsheet();
    var name = ss.getName()
    //UrlFetchApp.fetch("http://optimize-ev.rrbpg8t3fx.us-east-1.elasticbeanstalk.com/", options);
    // version 5 -- UrlFetchApp.fetch("http://optimize-ev7.3mxznjq7rb.us-east-1.elasticbeanstalk.com/", options);
    // version 12 -- UrlFetchApp.fetch("http://op12env.swjunczmms.us-east-1.elasticbeanstalk.com/", options);
    //UrlFetchApp.fetch("http://chewseNewApp2.hbc3xu33uf.us-west-2.elasticbeanstalk.com/", options);
    // UrlFetchApp.fetch("http://chewseSoftVendors.t9fnnauur5.us-west-2.elasticbeanstalk.com/", options);
    UrlFetchApp.fetch("52.23.252.18/" + name, options);
   
    
    // UrlFetchApp.fetch("http://optenv13.ghmqcrxyks.us-east-1.elasticbeanstalk.com/", options);
    //var json = prices.getContentText();
    //var rawdata = JSON.parse(json);
    //var rawdata = JSON.parse(prices.getContentText());
    //Logger.log(rawdata);
    //var data = [];
    //data.push(rawdata);
    //pr = addSheet("1-2hRZahevtF_k7Wpkd_XNyiNhFRRRjgTZRVq0Xef96w", "Prices");
    //pr.appendRow(data)
    SpreadsheetApp.getUi() // Or DocumentApp or FormApp.
       .alert('Results will post within 5-20 minutes');
    
    
  }
  
  function menuItem1a() {
    var options = {'muteHttpExceptions' : true};
  //UrlFetchApp.fetch("chewseComboApp.ms7sexhemc.us-west-2.elasticbeanstalk.com/hard/", options);
   UrlFetchApp.fetch("52.91.104.144/", options);
    SpreadsheetApp.getUi() // Or DocumentApp or FormApp.
       .alert('Results will post within 5-20 minutes');
  }
  //Create a Pivot table summarizing monthly meal assignments to each vendor and calculate COGS/GMV based on this table
  function menuItem2() {
    var active = SpreadsheetApp.getActiveSpreadsheet()
    var as = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
    //var asCD = as.getSheetByName('Cloud Data');
    var id = active.getId()
    var ss = addSheet(id, "Manual Summary");
    
    var ssPT = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
    
    summarizeMeals(id, as.getSheetId(), ss); 
    
  }
  
  //Create a Pivot table summarizing the amount of orders going to each vendor (columns) by each customer (rows)
  function menuItem3() {
    var options = {'muteHttpExceptions' : true};
    //var name = Browser.inputBox('Enter a short name for the sheet:');
    UrlFetchApp.fetch("54.235.31.27/", options);
      SpreadsheetApp.getUi() // Or DocumentApp or FormApp.
       .alert('Results will post within 5-20 minutes');
    
  }
  //Create a Pivot table summarizing the amount of orders going to each vendor (columns) by each customer (rows)
  function menuItem4() {
    var options = {'muteHttpExceptions' : true};
    //var name = Browser.inputBox('Enter a short name for the sheet:');
    UrlFetchApp.fetch("34.205.37.92/", options);
      SpreadsheetApp.getUi() // Or DocumentApp or FormApp.
       .alert('Results will post within 5-20 minutes');
    
  }
  
  function showSummarize(){
   
   
   var ss = SpreadsheetApp.getActiveSpreadsheet();
   var vendors = ss.getSheetByName("Vendors");
   var summary = ss.getSheetByName("Manual Summary");
   var deals = vendors.getRange("D1:E150").getValues();
   var range = summary.getRange("A6:D157").getValues();
   var menus = {}
   var clear = summary.getRange("D1:D150");
   clear.clear()
   /*for(var k=0; k<10; k++){
     arr = deals.getValues();
     Logger.log(arr[k][0]);
   }
   */
   
  
   
    for( var i=0; i<148; i++){
      for( var j=0; j<148; j++){
        Logger.log(range[i][1]);
        if(i>=1){
        if((range[i][0]== deals[j][1] || range[i-1][0]== deals[j][1])  && range[i][1] == deals[j][0]){
          //Logger.log("match");
        var currentVolume = range[i][2];
          
        var lookupVolumes = vendors.getRange(1+j, 9, 1, 21).getValues();
        var price = 0
        var t =0;
        //Logger.log(lookupVolumes[0][t]);
        
        while(lookupVolumes[0][t]<=currentVolume && t<6 && lookupVolumes[0][t]!=""){
          //Logger.log(lookupVolumes[0][t]);
          
          t +=1; 
        
          
          
          }
          Logger.log(price);
          if(t==6){
          price = lookupVolumes[0][12];
           t+=1;
          }
          else{
          step = 6;
          price = lookupVolumes[0][t+step];
          }
          while(price == ""){
            step -=1;
            price = lookupVolumes[0][t+step];
          }
          //Logger.log(price);
          var output =  summary.getRange("A6:D157").getCell(i+1, 4).setValue(price);
          Logger.log(price);
        }
          
    
  }
        else{
           if(range[i][0]== deals[j][1]  && range[i][1] == deals[j][0]){ 
        //Logger.log(range[i][1]);
        var currentVolume = range[i][2];
          
        var lookupVolumes = vendors.getRange(1+j, 9, 1, 21).getValues();
        var price = 0
        var t =0;
        //Logger.log(lookupVolumes[0][t]);
        
        while(lookupVolumes[0][t]<=currentVolume && t<6 && lookupVolumes[0][t]!=""){
          //Logger.log(lookupVolumes[0][t]);
          
          t +=1; 
        
          
          
          }
          
          if(t==6){
          price = lookupVolumes[0][12];
           t+=1;
          }
          else{
          step = 6;
          price = lookupVolumes[0][t+step];
          }
          while(price == ""){
            step -=1;
            price = lookupVolumes[0][t+step];
          }
          //Logger.log(price);
          var output =  summary.getRange("A6:D157").getCell(i+1, 4).setValue(price);
          
        } 
          }
        
        
        
      
    }
    }
  }
  
  function calcSummarize(){
   
   
   var ss = SpreadsheetApp.getActiveSpreadsheet();
   var vendors = ss.getSheetByName("Vendors");
   var summary = ss.getSheetByName("Manual Summary");
   var deals = vendors.getRange("D1:E150").getValues();
   var range = summary.getRange("A6:D157").getValues();
   var menus = {}
   var clear = summary.getRange("D1:D157");
   var prices = []
   var volumes = []
   //clear.clear()
   /*for(var k=0; k<10; k++){
     arr = deals.getValues();
     Logger.log(arr[k][0]);
   }
   */
   
  
   
    for( var i=0; i<148; i++){
      for( var j=0; j<148; j++){
        if(i>=1){
        if((range[i][0]== deals[j][1] || range[i-1][0]== deals[j][1])  && range[i][1] == deals[j][0]){
        Logger.log(range[i][1]);
        var currentVolume = range[i][2];
          
        var lookupVolumes = vendors.getRange(1+j, 9, 1, 21).getValues();
        var price = 0
        var t =0;
        Logger.log(lookupVolumes[0][t]);
        
        while(lookupVolumes[0][t]<=currentVolume && t<6 && lookupVolumes[0][t]!=""){
          Logger.log(lookupVolumes[0][t]);
          
          t +=1; 
        
          
          
          }
          
          if(t==6){
          price = lookupVolumes[0][12];
           t+=1;
          }
          else{
          step = 6;
          price = lookupVolumes[0][t+step];
          }
          while(price == ""){
            step -=1;
            price = lookupVolumes[0][t+step];
          }
          //Logger.log(price);
          //var output =  summary.getRange("A6:D100").getCell(i+1, 4).setValue(price)
           prices.push(price);
          volumes.push(currentVolume);
        }
          
    
  }
        else{
           if(range[i][0]== deals[j][1]  && range[i][1] == deals[j][0]){ 
        Logger.log(range[i][1]);
        var currentVolume = range[i][2];
          
        var lookupVolumes = vendors.getRange(1+j, 9, 1, 21).getValues();
        var price = 0
        var t =0;
        Logger.log(lookupVolumes[0][t]);
        
        while(lookupVolumes[0][t]<=currentVolume && t<6 && lookupVolumes[0][t]!=""){
          Logger.log(lookupVolumes[0][t]);
          
          t +=1; 
        
          
          
          }
          
          if(t==6){
          price = lookupVolumes[0][lookupVolumes[0].length];
           t+=1;
          }
          else{
          step = 6;
          price = lookupVolumes[0][t+step];
          }
          while(price == ""){
            step -=1;
            price = lookupVolumes[0][t+step];
          }
          //Logger.log(price);
          //var output =  summary.getRange("A6:D100").getCell(i+1, 4).setValue(price)
          prices.push(price);
          volumes.push(currentVolume);
        } 
          }
        
      
    }
    }
    
        totalcost = 0;
        for(var h=0; h<prices.length; h++){
          if(prices[h] != null){
          totalcost += prices[h]*volumes[h];
        
          }
        }
        Logger.log(totalcost);
    Logger.log(prices);
    Logger.log(volumes);
    summary.getRange(1,9).setValue(totalcost);
    
  }
  
  
  function addSheet(spreadsheetId, name) {
    var requests = [{
      "addSheet": {
        "properties": {
          "title": name,
          "gridProperties": {
            "rowCount": 100,
            "columnCount": 12
          },
          "tabColor": {
            "red": 1.0,
            "green": 0.3,
            "blue": 0.4
          }
        }
      }
    }];
  
    var response = Sheets.Spreadsheets.batchUpdate({'requests': requests}, spreadsheetId);
    return response.replies[0].addSheet.properties.sheetId;
  }
  
  
  function summarizeMeals(
      spreadsheetId, pivotSourceDataSheetId, destinationSheetId) {
    var requests = [{
      "updateCells": {
        "rows": {
          "values": [
            {
              "pivotTable": {
                "source": {
                  "sheetId": pivotSourceDataSheetId,
                  "startRowIndex": 0,
                  "startColumnIndex": 0,
                  "endRowIndex": 2000,
                  "endColumnIndex": 21
                },
                "rows": [
                  {
                    "sourceColumnOffset": 8,
                    "showTotals": true,
                    "sortOrder": "ASCENDING",
                    "valueBucket": {
                      "buckets": [
                        {
                          "stringValue": "West"
                        }
                      ]
                    }
                  },
                  
                ],
                
                "values": [
                  {
                    "summarizeFunction": "SUM",
                    "sourceColumnOffset": 6
                  }
                ],
                "valueLayout": "HORIZONTAL"
              }
            }
          ]
        },
        "start": {
          "sheetId": destinationSheetId,
          "rowIndex": 2,
          "columnIndex": 0
        },
        "fields": "pivotTable"
      }
    }];
  
    var response = Sheets.Spreadsheets.batchUpdate({'requests': requests}, spreadsheetId);
    
    var requests = [{
      "updateCells": {
        "rows": {
          "values": [
            {
              "pivotTable": {
                "source": {
                  "sheetId": pivotSourceDataSheetId,
                  "startRowIndex": 0,
                  "startColumnIndex": 0,
                  "endRowIndex": 2000,
                  "endColumnIndex": 21
                },
                "rows": [
                  {
                    "sourceColumnOffset": 8,
                    "showTotals": true,
                    "sortOrder": "ASCENDING",
                    "valueBucket": {
                      "buckets": [
                        {
                          "stringValue": "West"
                        }
                      ]
                    }
                  },
                   {
                    "sourceColumnOffset": 5,
                    "showTotals": true,
                    "sortOrder": "ASCENDING",
                    "valueBucket": {
                      "buckets": [
                        {
                          "stringValue": "West"
                        }
                      ]
                    }
                  },
                  
                ],
                
                "values": [
                  {
                    "summarizeFunction": "COUNT",
                    "sourceColumnOffset": 4
                  },
                  {
                    "summarizeFunction": "SUM",
                    "sourceColumnOffset": 6
                  }
                ],
                "valueLayout": "HORIZONTAL"
              }
            }
          ]
        },
        "start": {
          "sheetId": destinationSheetId,
          "rowIndex": 2,
          "columnIndex": 10
        },
        "fields": "pivotTable"
      }
    }];
  
    var response =
        Sheets.Spreadsheets.batchUpdate({'requests': requests}, spreadsheetId);
    
  }
  
  
  
  function analyzeVendorVariety(
      spreadsheetId, pivotSourceDataSheetId, destinationSheetId) {
    var requests = [{
      "updateCells": {
        "rows": {
          "values": [
            {
              "pivotTable": {
                "source": {
                  "sheetId": pivotSourceDataSheetId,
                  "startRowIndex": 0,
                  "startColumnIndex": 0,
                  "endRowIndex": 2000,
                  "endColumnIndex": 8
                },
                "rows": [
                  {
                    "sourceColumnOffset": 1,
                    "showTotals": true,
                    "sortOrder": "ASCENDING",
                    "valueBucket": {
                      "buckets": [
                        {
                          "stringValue": "West"
                        }
                      ]
                    }
                  },
                  
                ],
                "columns": [
                  {
                    "sourceColumnOffset": 6,
                    "sortOrder": "ASCENDING",
                    "showTotals": true,
                    "valueBucket": {}
                  }
                ],
                "values": [
                  {
                    "summarizeFunction": "COUNT",
                    "sourceColumnOffset": 5
                  }
                ],
                "valueLayout": "HORIZONTAL"
              }
            }
          ]
        },
        "start": {
          "sheetId": destinationSheetId,
          "rowIndex": 2,
          "columnIndex": 0
        },
        "fields": "pivotTable"
      }
    }];
  
    var response =
        Sheets.Spreadsheets.batchUpdate({'requests': requests}, spreadsheetId);
    // The Pivot table will appear anchored to cell A50 of the destination sheet.
  }
  
  function formatRisk(spreadsheetId)
   {
    var active = SpreadsheetApp.getActiveSpreadsheet()
    var id = active.getID()
    var requests = [
      {
        "addConditionalFormatRule": {
          "rule": {
            "ranges": [
              {
                "sheetId": spreadsheetId,
                "startColumnIndex": 0,
                "endColumnIndex": 40,
              },
              
            ],
            "booleanRule": {
              "condition": {
                "type": "NUMBER_GREATER",
                "values": [
                  {
                    "userEnteredValue": "1"
                  }
                ]
              },
              "format": {
                "backgroundColor": {
                  "red": 0.83,
                  "green": 0.68,
                  "blue": 0.1,
                  "alpha": 0.75,
                }
              }
            }
          },
          "index": 0
        }
      }
    ]
    var response =
        Sheets.Spreadsheets.batchUpdate({'requests': requests}, id);
  } 
  
    
  