module EGRIN2 {
    /* A job id defined by the service */
    typedef string job_id;
    typedef int boolean;

    typedef structure {
        string name;
        list<string> data;
    } SetEnrichmentSet;

    typedef structure {
        string blocks;
        string inclusion_blocks;
        string exclusion_blocks;
    } BlockDefinitions;

    typedef structure {
        list<string> row_names;
        list<string> col_names;
        list<list<float>> values;
    } SimpleGeneExpressionMatrix;

    typedef structure {
        string seq_name;
        boolean reverse;
        int start;
        float pvalue;
    } MotifSite;

    typedef structure {
        float a;
        float c;
        float g;
        float t;
    } PSSMRow;

    typedef structure {
        string seqtype;
        int motif_num;
        float evalue;
        list<MotifSite> sites;
        list<PSSMRow> pssm_rows;
    } Motif;

    typedef structure {
        float residual;
        int num;
        list<string> row_names;
        list<string> col_names;
        list<Motif> motifs;
    } Bicluster;

    typedef structure {
        string name;
        float pvalue;
    } CoremColumn;

    typedef structure {
        string row1;
        string row2;
    } CoremEdge;

    typedef structure {
        int num;
        float density;
        float weighted_density;
        list<string> rows;
        list<CoremColumn> columns;
        list<CoremEdge> edges;
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

    /*
     * Starts an ensemble run. The state of the computation can be obtained by
     * querying the UserAndJobState service using the returned job id
     *
     * Notes:
     * We need to propagate the authentication token, marking this function
     * as "authentication required" will put the token into the context object
     */
    authentication required;
    funcdef run_ensemble(EnsembleParams params) returns (job_id jobid);
};
