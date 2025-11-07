<h1>create-dmp</h1>

App for creating new data management plans (projects, DMP:s) with pre-filled data in Chalmers DS Wizard (dsw.chalmers.se), using a tab separated file with metadata and new Project records in Chalmers CRIS (research.chalmers.se), possibly enriched with data from a secondary source, such as SweCRIS or GDP.

Assumes an input file in the following format (tab separated, utf-8/unix lf), especially note name orientation (inverted) and e-mail address used (should ideally correspond with the primary Chalmers e-mail returned by the Idp, but the app will try and look this up from Chalmers PDB):        
2021-12345\tEinstein Albert\teinstein@chalmers.se\n           
      
If you copy or export the input data from MS Excel, you might have to use a text editor like Notepad++ to make sure the input file uses UTF-8 and Unix type line feeds. See also sample-input.txt.     

The app will try and create the user (and set permissions) if not already found in DSW. It will also (if selected) send e-mails to the researchers after DMP and CRIS project have been created, using a set of pre-defined, funder specific templates.   
Supported funders are currently VR and Formas only, adding more funders require (minor) code changes.         

DSW settings (paths) in create-new-dmp.conf need to be adjusted to the selected DSW KM.    

Please use the staging environment (dsw-staging.xxx) and (at least initially) set send_emails to "false" when testing!  

*Requirements*   
* Python >= 3.8  
* DS Wizard v. 4.22 or later (replace IntegrationLegacyType with IntegrationType if DSW version is < 4.22.0) and a user ID with admin API access       
* Access to Chalmers PDB API    
* Mail server for outgoing mail (SMTP)   
* Access to SweCRIS and/or GDP API:s   

*Install and run the app*   
* Use `git clone https://github.com/ChalmersLibrary/create-dmp.git´ to download the code into a local directory.    
* Create an **.env** settings file in the /create_dmp sub-directory. Use env_example as a template.   
* Install the app by running `pip install .´ in the app root directory.   
* Execute directly from command line, i.e. `create-dmp -i formas_251030.txt -f formas´   
* Input files should ideally be put in the app root directory, otherwise the path has to be specified on the command line (log files are created there too).  

*Options*    
* -i, --infile - Input file, tab-delimited, with columns (no headers): ProjectID, Name (inverted), Email. (required)    
* -f, --funder - Funder name, e.g. formas or vr, (required)    
* -u, --updateCRIS - Create CRIS project records (y/n), default=y
* -e, --sendEmails - Send e-mail alerts to researchers automatically (y/n) default=n
* -v, --verbose - Enable verbose output (y/n), default=n  
* -h, --help    
    
*Uninstall*    
You can uninstall the app by running `pip uninstall create-dmp´ from the root directory. Please note that you will need to re-install the app when something has been updated.           

This app can be used in conjunction with other Chalmers DS Wizard services, such as:   
https://github.com/ChalmersLibrary/dsw2es        
https://github.com/ChalmersLibrary/cth-dmps-api   

