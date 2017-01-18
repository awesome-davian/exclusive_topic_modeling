# TweetsToTiles
Converts MongoDB collection of tweets into geospatial and temporal output blocks, currently in the form of MongoDB collections

# Installation
TweetsToTiles uses Ant to build the Java project. Make sure Ant is installed on your system and then run the following from within the TweetsToTiles repository:
```
ant jar
```

This will produce an executable jar file located at dist/TweetsToTiles.jar. Running the application without any command line arguments:
```
java -jar dist/TweetsToTiles.jar
```

You should see the following ouptut: 
```
Usage: java -jar /path/to/TweetsToTiles.jar
		 --db             database containing target collection
		 --col            collection containing tweets
		 --levels         tile levels to extract (csv list of tile levels)
		[--time_interval] time period by which to segment {year, month, week, day}
		[--host]          host for mongodb (defaults to localhost)
		[--port]          port for mongodb (defaults to 27017)
		[--output_host]   host for output mongodb (defaults to localhost)
		[--output_port]   port for output mongodb (defaults to 27017)
```

# Usage
The db, col, and levels command line arguments are required, and the rest are optional. The application will separate the input collection into individual time/tile segmented collections, which will be deposited into a database named {db}_tiles, where {db} is the input database. 

For example, TweetsToTiles could be used to separate the input dataset into segments per week and tile for tile levels 12, 13, and 14:
```
java -jar dist/TweetsToTiles.jar --db twitter --col tweets --levels 12,13,14 --time_interval week
```
The application will use the MongoDB instance at localhost:27017 to connect to the tweets collection in the twitter database and extract the appropriate tweets in to a new database called twitter_tiles. The collection names will be similar to the following sample:
```
...
level13_w10_281324 - representing level 13, week 10, tile 281324
level13_w11_303215
level13_w12_316533
level13_w13_321342
...
```

Each of the collections contains all tweets in their original JSON.


