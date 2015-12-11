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

        string target_ws;
        string result_name;
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
