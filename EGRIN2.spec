module EGRIN2 {
    /* A job id defined by the service */
    typedef string job_id;
    typedef structure {
        string name;
        list<string> data;
    } SetEnrichmentSet;

    typedef structure {
        string blocks;
        string inclusion_blocks;
        string exclusion_blocks;
    } BlockDefinitions;

    /**********************************************************/
    /* Result definitions         START                       */
    /* all information currently generated during EGRIN2      */
    /* runs                                                   */
    /**********************************************************/
    typedef structure {
        list<string> row_names;
        list<string> col_names;
        list<list<double>> values;
    } SimpleGeneExpressionMatrix;

    typedef structure {
        string seq_name;
        bool reverse;
        int start;
        double pvalue;
    } MotifSite;

    typedef structure {
        double a, c, g, t;
    } PSSMRow;

    typedef structure {
        string seqtype;
        int motif_num;
        double evalue;
        list<MotifSite> sites;
        list<PSSMRow> pssm_rows;
    } Motif;

    typedef structure Bicluster {
        double residual;
        int num;
        list<string> row_names;
        list<string> col_names;
        list<Motif> motifs;
    };

    typedef structure {
        string name;
        double pvalue;
    } CoremColumn;

    typedef structure {
        string row1;
        string row2;
    } CoremEdge;

    typedef structure {
        int num;
        double density;
        double weighted_density;
        list<string> rows;
        list<CoremColumn> columns;
        list<string
    } Corem;

    typedef structure {
        string date_added;
        string start_time;
        string finish_time;
        int num_iterations;
        string organism;
        string species;
        list<string> row_names;
        list<string> column_names;
        list<Bicluster> clusters;
    } EnsembleRun;
    /*
    The parameters to run an ensemble.
    organism - a KEGG code specifying the organism
    ratios   - gene expressions in tab separated format
    num_runs - number of runs
    */
    typedef structure {
        string organism;
        string ratios;
        int num_runs;
        int min_cols;
        BlockDefinitions block_defs;
        string pipeline;
        list<SetEnrichmentSet> setenrichment_sets;
    } EnsembleParams;
    /**********************************************************/
    /* Result definitions    END                              */
    /**********************************************************/

    /*
     * Starts an ensemble run. The state of the computation can be obtained by
     * querying the UserAndJobState service using the returned job id
     *
     * Notes:
     * We need to propagate the authentication token, marking this function
     * as "authentication required" will put the token into the context object
     */
    funcdef run_ensemble(EnsembleParams params) returns (job_id jobid) authentication required;
};
