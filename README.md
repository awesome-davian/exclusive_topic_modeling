# Exclusive Topic Modeling
Compute exclusive topic modeling with reference to surrounding tiles.

## Usage

### Tile Generator
* **Rawdata to MongoDB**
Rawdata path: `/scratch/salt`
Usage Example:
```
mongoimport --db salt_rawdata_131231 --collection tweets --file 2013_12_31
```

* **Run TweetToTiles**
Binary path: `/scratch/salt/exclusive_topic_modeling/tile_generator/TweetsToTiles`
Compile: `ant jar`
Usage Example:
```
java -jar ./dist/TweetsToTiles.jar --db salt_rawdata_131231 --col tweets --levels 9,10,11,12,13 --time_interval week
```

* **Create the term-document matrices**
```
python termdoc_gen.py
```

* **Precompute the topic modeling for each tile**
```
python topic_modeling_module_all.py
```

### Topic Modeling System
* **Run Topic Modeling System**
```
python topic_modeling_module.py
```