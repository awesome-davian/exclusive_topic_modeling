package edu.gatech.xdata.uncharted.tweets;

import java.util.List;

/**
 *
 * @author richardboyd, ashleybeavers
 */
public class Options 
{
    // inputs needed for mongo input
    public String host;
    public int port = 0;
    public String db;
    public String col;
    
    // inputs needed for mongo output
    public String output_host;
    public int output_port = 0;
    
    // output dir for file option
    public String outdir;
    
    public List<Integer> levels;
    public String time_interval;
    
    public boolean showHelp;
}
