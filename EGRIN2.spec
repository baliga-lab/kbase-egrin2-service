module EGRIN2 {
    /* A job id defined by the service */
    typedef string job_id;

    /*
    The parameters to run an ensemble.
    organism - a KEGG code specifying the organism
    ratios   - gene expressions in tab separated format
    num_runs - number of runs
    config   - a cmonkey ini file
    */
    typedef structure {
	string organism;
	string ratios;
	int num_runs;
	string config;
    } EnsembleParams;

    funcdef run_ensemble(EnsembleParams params) returns (job_id jobid);
};
