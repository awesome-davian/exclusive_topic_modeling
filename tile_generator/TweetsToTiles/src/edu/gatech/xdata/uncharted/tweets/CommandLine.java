package edu.gatech.xdata.uncharted.tweets;

import java.io.File;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

/**
 *
 * @author richardboyd, ashleybeavers
 */
public class CommandLine 
{  
    private final String ARG_HOST           = "host";
    private final String ARG_PORT           = "port";
    private final String ARG_DB             = "db";
    private final String ARG_COL            = "col";
    private final String ARG_OUTDIR         = "outdir";
    private final String ARG_OUTPUT_HOST    = "output_host";
    private final String ARG_OUTPUT_PORT    = "output_port";
    private final String ARG_LEVELS         = "levels";
    private final String ARG_TIME           = "time_interval";
    private final String ARG_HELP           = "help";
    
    public CommandLine() {} 
    
    
    public void printOpts(Options opts) 
    {
        System.out.println("Command line options: \n");
        System.out.print("\t         " + ARG_HOST + ": ");
        System.out.println(opts.host);
        System.out.print("\t         " + ARG_PORT + ": ");
        System.out.println(opts.port);
        System.out.print("\t           " + ARG_DB + ": ");
        System.out.println(opts.db);
        System.out.print("\t          " + ARG_COL + ": ");
        System.out.println(opts.col);
        System.out.print("\t          " + ARG_OUTDIR + ": ");
        System.out.println(opts.outdir);
        System.out.print("\t  " + ARG_OUTPUT_HOST + ": ");
        System.out.println(opts.output_host);
        System.out.print("\t  " + ARG_OUTPUT_PORT + ": ");
        System.out.println(opts.output_port);
        System.out.print("\t       " + ARG_LEVELS + ": ");
        System.out.println(opts.levels);
        System.out.print("\t" + ARG_TIME + ": ");
        System.out.println(opts.time_interval);
        System.out.println();
    }
    
    public void showHelp() 
    {    
        String usage = "java -jar /path/to/TweetsToTiles.jar\n"
                + "\t\t --" + ARG_DB + "             database containing target collection\n"
                + "\t\t --" + ARG_COL + "            collection containing tweets\n"
                + "\t\t --" + ARG_LEVELS + "         tile levels to extract\n"
                + "\t\t[--" + ARG_TIME + "] time period by which to segment {year, month, week, day}\n"
                + "\t\t[--" + ARG_HOST + "]          host for mongodb\n"
                + "\t\t[--" + ARG_PORT + "]          port for mongodb\n"
                + "\t\t[--" + ARG_OUTDIR + "]        output directory\n"
                + "\t\t[--" + ARG_OUTPUT_HOST + "]   host for output mongodb\n"
                + "\t\t[--" + ARG_OUTPUT_PORT + "]   port for output mongodb\n";
                
        System.out.println("\nUsage: " + usage);
    }
    
    public boolean isValid(Options opts) 
    {
        
        if (null == opts.db) {
            System.out.println("A database must be specified.");
            return false;
        }

        if (null == opts.col) {
            System.out.println("A collection must be specified.");
            return false;
        }
        if (null != opts.outdir) {
            File outdir = new File(opts.outdir);
            if (!outdir.exists()) {
                outdir.mkdir();
            }
        }

        if (null == opts.output_host) {
            opts.output_host = opts.host;
        }         

        if (0 == opts.output_port) {
            opts.output_port = opts.port;
        }

        if (null == opts.levels) {
            System.out.println("At least one level must be specified.");
            return false;
        } 
        
        if (!opts.time_interval.equals("")) {
            List<String> options = Arrays.asList("year","month","week","day");
            if ( !options.contains(opts.time_interval.toLowerCase())){
                System.out.println("Time interval must be one of the following:"
                        + " {year, month, week, day}.");
                return false;
            }
        }
        return true;
    }
    

    
    public boolean parse(String[] args, Options opts) 
    {        
        // set defaults
        opts.host = "localhost";
        opts.port = 27017;
        opts.time_interval = "";
                
        int k=0;
        boolean ok = true;
        
        while (k < args.length) 
        {
            char c0 = args[k].charAt(0);
            char c1 = args[k].charAt(1);
            
            if ( ('-' == c0) && ( ('h' == c1) || ('H' == c1)))
            {
                // user specified short help option
                opts.showHelp = true;
                break;
            }             
            else if ( ('-' == c0) && ('-' == c1)) 
            {
                // found two dashes, so extract arg name                
                String thisArg = args[k].substring(2);
                String lowercaseArg = thisArg.toLowerCase();
                
                // arg requires an option
                if (args.length < k+1) 
                {
                    System.err.println("Missing option for argument " + thisArg);
                    return false;
                }                
                
                switch (lowercaseArg) 
                {
                    case ARG_DB:
                        opts.db = args[k+1];
                        k += 2;
                        break;
                    case ARG_COL:
                        opts.col = args[k+1];
                        k += 2;
                        break;
                    case ARG_LEVELS:
                        opts.levels = new ArrayList<>();
                        for (String s : args[k+1].split("\\s*,\\s*")) {
                            opts.levels.add(Integer.parseInt(s));
                        }
                        k += 2;
                        break;
                    case ARG_TIME:                            
                        opts.time_interval = args[k+1];
                        k += 2;
                        break;
                    case ARG_HOST:                            
                        opts.host = args[k+1];
                        k += 2;
                        break;
                    case ARG_PORT:
                        opts.port = Integer.parseInt(args[k+1]);
                        k += 2;
                        break;
                    case ARG_OUTPUT_HOST:                            
                        opts.output_host = args[k+1];
                        k += 2;
                        break;
                    case ARG_OUTDIR:                            
                        opts.outdir = args[k+1];
                        k += 2;
                        break;
                    case ARG_OUTPUT_PORT:
                        opts.output_port = Integer.parseInt(args[k+1]);
                        k += 2;
                        break;
                    case ARG_HELP:
                        opts.showHelp = true;
                        break;
                    default:
                        System.err.println("Unknown option: " + args[k].substring(2));
                        ok = false;
                        break;
                }
                
                if (!ok)
                    return false;
            }
            else
            {
                System.err.println("Invalid command line.");
                return false;
            }
            
            if (opts.showHelp)
                break;
        }
        
        return true;
    }
}
