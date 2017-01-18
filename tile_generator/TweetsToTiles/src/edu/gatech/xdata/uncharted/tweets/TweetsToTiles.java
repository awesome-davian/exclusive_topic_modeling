package edu.gatech.xdata.uncharted.tweets;

import java.awt.geom.Point2D;
import java.io.IOException;
import java.io.PrintWriter;
import java.net.UnknownHostException;
import java.text.ParseException;
import java.text.SimpleDateFormat;
import java.util.Calendar;
import java.util.Date;
import java.util.HashMap;
import java.util.List;
import java.util.Set;

import org.json.JSONObject;

import com.mongodb.BasicDBObject;
import com.mongodb.DB;
import com.mongodb.DBCollection;
import com.mongodb.DBCursor;
import com.mongodb.DBObject;
import com.mongodb.MongoClient;
import com.mongodb.MongoTimeoutException;
import com.oculusinfo.binning.TileIndex;
import com.oculusinfo.binning.WebMercatorTilePyramid;

public class TweetsToTiles {

    private static final String VERSION = "0.2";
    private static int docsIndexed = 0;

    

    static DBCursor getCursor(Options opts) throws UnknownHostException {

        /*	mchoi
        MongoClient mongoClient = new MongoClient(opts.host, opts.port);
        DB db = mongoClient.getDB(opts.db);
        DBCollection coll = db.getCollection(opts.col);
        BasicDBObject query = new BasicDBObject();
        BasicDBObject subquery = new BasicDBObject();
        subquery.append("$ne", null);
        query.append("geo", subquery);
        query.append("twitter_lang","en");
        DBCursor cursor = coll.find(query);
        return cursor;*/
        
        MongoClient mongoClient = new MongoClient(opts.host, opts.port);
        DB db = mongoClient.getDB(opts.db);
        DBCollection coll = db.getCollection(opts.col);
        BasicDBObject query = new BasicDBObject();
        BasicDBObject subquery = new BasicDBObject();
        subquery.append("$ne", null);
        query.append("geo", subquery);
        query.append("lang","en");
        DBCursor cursor = coll.find(query);
        return cursor;
    }
    public static Date getTwitterDate(String date) throws ParseException {

        final String TWITTER="EEE MMM dd HH:mm:ss ZZZZZ yyyy";
    	// final String TWITTER="yyyy-MM-dd'T'HH:mm:ss.SSS'Z'";	// mchoi
        SimpleDateFormat sf = new SimpleDateFormat(TWITTER);
        sf.setLenient(true);
        return sf.parse(date);
    }

    static DB getOutputDB(Options opts) throws UnknownHostException {
        MongoClient mongoClient = new MongoClient(opts.output_host, opts.output_port);
        DB db = mongoClient.getDB(opts.col + "_tiles131225");
        return db;

    }
    
    static boolean collectionsExists(DB db, final String collectionName) {
    	Set<String> collectionNames = db.getCollectionNames();
        for (final String name : collectionNames) {
            if (name.equalsIgnoreCase(collectionName)) {
                return true;
            }
        }
        return false;
    }
    
    static Object getNextSequence(DB db, String col_name) {
    	// System.out.println("getNextSequence: " + col_name);
    	DBCollection countersCollection = db.getCollection("counters");
    	
    	if (countersCollection.count() == 0) {
        	// if collection is not already exist --> create
    		DBObject query = new BasicDBObject("_id", col_name).append("seq", 0);
    		countersCollection.insert(query);
    		// System.out.println("First: " + col_name);
    		
    	} else if (countersCollection.findOne(new BasicDBObject("_id", col_name)) == null) {
    		DBObject query = new BasicDBObject("_id", col_name).append("seq", 0);
    		countersCollection.insert(query);
    		// System.out.println("Second: " + col_name);
    	}
    	
    	// if collection is already exist
    	BasicDBObject query = new BasicDBObject("_id", col_name);
    	BasicDBObject update = new BasicDBObject();
    	update.put("$inc",  new BasicDBObject("seq", 1));
    	DBObject result = countersCollection.findAndModify(query, null, null, false, update, true, false);
    	
    	return result.get("seq");
    }

    static void segmentTweets(Options opts)
            throws MongoTimeoutException, IOException, ParseException {
    	
        DBCursor cursor = getCursor(opts);
        WebMercatorTilePyramid wmtd = new WebMercatorTilePyramid();
        DB outputDB = getOutputDB(opts);
        long start = System.nanoTime();
        HashMap<TileIndex, PrintWriter> tiletoFile = new HashMap<>();

        System.out.println("cursor.size(): " + cursor.size());
        
        try {
//            if (cursor.size() == 0) {
//                System.out.println("exception?");
//                throw new UnsupportedOperationException();
//            } else {
                while (cursor.hasNext()) {
                	// read the next tweet from mongo
                    DBObject tweetJSON = cursor.next();
                    Boolean retweeted, hasText, containsUrl;
                    retweeted = hasText = containsUrl = false;
                    String geoType, textSrc;
                    geoType = textSrc = null;
                    Date date;
                    Calendar cal = Calendar.getInstance();
                    
                    long retweetCount = 0;

                    /*if (tweetJSON.get("retweeted").toString().equals("true")) {
                        retweeted = true;
                    }*/
                    if (tweetJSON.get("text") != null) {
                        textSrc = "text";
                    } else if (tweetJSON.get("body") != null) {
                        textSrc = "body";
                    }
                    if (tweetJSON.get("retweet_count") != null) {
                        retweetCount = new Long(tweetJSON.get("retweet_count").toString());
                        if (retweetCount > 0)
                        	retweeted = true;
                    }
                    
//                    if (tweetJSON.get("possibly_sensitive") != null) {
//                        containsUrl = true;
//                    }

                    if (tweetJSON.get("coordinates") != null) {
                        geoType = "coordinates";
                    }
                    if (tweetJSON.get("geo") != null) {
                        geoType = "geo";
                    }
                    if (!retweeted && !containsUrl && geoType != null && textSrc != null) {
                        assert (retweetCount == 0);
                        double x = Double.NaN, y = Double.NaN;
                        BasicDBObject coordinatejson = null;
                        JSONObject jso = new JSONObject(tweetJSON);
                        List<Double> coordinates = null;
                        switch (geoType) {
                            case "coordinates":
                                coordinatejson = (BasicDBObject) tweetJSON.get("coordinates");
                                coordinates = (List<Double>) coordinatejson.get("coordinates");
                                x = ((Number) coordinates.get(0)).doubleValue();
                                y = ((Number) coordinates.get(1)).doubleValue();
                                break;
                            case "geo":
                                coordinatejson = (BasicDBObject) tweetJSON.get("geo");
                                coordinates = (List<Double>) coordinatejson.get("coordinates");
                                x = ((Number) coordinates.get(0)).doubleValue();
                                y = ((Number) coordinates.get(1)).doubleValue();
                                break;
                        }
                        assert (x != Double.NaN && y != Double.NaN);
                        String tweettext = null;
                        switch (textSrc) {
                            case "text":
                                tweettext = tweetJSON.get("text").toString();
                                break;
                            case "body":
                                tweettext = tweetJSON.get("body").toString();
                                break;
                        }
                        assert (tweettext != null);

                        // determine what tile the tweet belongs to at this level    
                        for (int level : opts.levels) {
                            TileIndex tweetTile = wmtd.rootToTile(new Point2D.Double(x,
                                    y), level);

                            //construct the appropriate collection name
                            date = getTwitterDate(tweetJSON.get("created_at").toString());
                            // date = getTwitterDate(tweetJSON.get("postedTime").toString());	// mchoi
                            cal.setTime(date);
                            String interval = "";
                            if (opts.time_interval.equals("year")) {
                                interval += Integer.toString(cal.get(Calendar.YEAR));
                                interval += "_";
                            }
                            else if (opts.time_interval.equals("month")) {
                                interval += Integer.toString(cal.get(Calendar.YEAR));
                                interval += "_m";
                                interval += Integer.toString(cal.get(Calendar.MONTH));
                                interval += "_";
                            }
                            else if (opts.time_interval.equals("week")) {
                                interval += Integer.toString(cal.get(Calendar.YEAR));
                                interval += "_w";
                                interval += Integer.toString(cal.get(Calendar.WEEK_OF_YEAR));
                                interval += "_";
                            }
                            else if (opts.time_interval.equals("day")) {
                                interval += Integer.toString(cal.get(Calendar.YEAR));
                                interval += "_d";
                                interval += Integer.toString(cal.get(Calendar.DAY_OF_YEAR));
                                interval += "_";
                            }

                            String output_name = "level" + Integer.toString(level) + "_"
                                    + interval + tweetTile.hashCode() + "_raw";
                            
                            System.out.println(output_name);

                            //insert tweet json into the appropriate collection
                            DBCollection outputCol = outputDB.getCollection(output_name);
                            if (null == opts.outdir){
                            	tweetJSON.put("_id", getNextSequence(outputDB, output_name));
                            	outputCol.insert(tweetJSON);
                            } else {
                                PrintWriter filetoWrite;
                                if (tiletoFile.containsKey(output_name)) {
                                	
                                    filetoWrite = tiletoFile.get(output_name);
                                } else {
                                	
                                    String filename = opts.outdir + "//" 
                                            + output_name + ".json";
                                    filetoWrite = new PrintWriter(
                                                    filename);
                                    tiletoFile.put(tweetTile, filetoWrite);
                                }
                                filetoWrite.write(tweetJSON.toString());
//                                filetoWrite.write("{\"text\":\"" + tweettext + "\"}");
                                filetoWrite.write("\n");
                                filetoWrite.flush();
                            }
                        }
                        ++docsIndexed;
                        if (0 == (docsIndexed % 1000)) {
                            System.out.print("Docs analyzed and indexed: " + docsIndexed + "\r");
                            System.out.flush();
                        }
                    }
                }
                long end = System.nanoTime();
                double elapsed = (end - start) * 1.0e-9;

                System.out.println("\n\nIndexed " + docsIndexed + " documents.");
                System.out.printf("Elapsed time: %.2f seconds, avg. rate: %.2f docs/s.\n\n",
                        elapsed, docsIndexed / elapsed);
//            }

        } catch (MongoTimeoutException mte) {
            System.out.println("Timed out while waiting to connect."
                    + "\nEnsure that the host/port/database/collection "
                    + "configuration is correct.");

        } catch (UnsupportedOperationException uoe) {
            System.out.println("\nWARNING: Cursor returned with 0 documents - "
                    + "ensure that the database/collection \n"
                    + "configuration is correct.");
        } finally {
            cursor.close();
        }

    }

    public static void main(String[] args) throws IOException, ParseException {
        Options opts = new Options();
        CommandLine commandLine = new CommandLine();
        
        // if no command line options specified, user wants help
        if (0 == args.length) {
            commandLine.showHelp();
            System.exit(0);
        }

        // extract command line args and store in opts
        if (!commandLine.parse(args, opts)) {
            System.exit(1);
        }

        if (opts.showHelp) {
            commandLine.showHelp();
            System.exit(0);
        }

        // validate all command line options
        if (!commandLine.isValid(opts)) {
            System.exit(1);
        }

        System.out.println("\nTweetsToTiles version " + VERSION + ".\n");
        commandLine.printOpts(opts);
        segmentTweets(opts);
    }
}
