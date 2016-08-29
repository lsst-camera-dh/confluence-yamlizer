## confluence-yamlizer

This tool was developed for Python 2.7.3, in Cygwin.

Tested on SLAC rhel6-32 (RedHatEnterpriseServer 6.8, Python 2.7.2)

For usage:
```bash
python confyamlizer.py -h
```

### Dependencies, Installing
#### Hand-rolled libraries (in ./lib)

Please set PYTHONPATH as needed.

* confluence/confluence_fetcher_rest
  * Hard-coded Confluence login credentials in here
* tinyxml
* tinylogging
* https

#### Third party libraries

* lxml 3.3.1
* requests 2.2.1

#### Directory structure

* The main script, confyamlizer.py, assumes ./src and ./config subdirectories.

### Page parsing requirements

* For Prerequisite table (maps to Prerequisites YAML tag), a table with cell 0,0 containing "PrerequisiteType"
   * PREPARATION prerequisite type is supported. CONSUMABLE should work. TEST_EQUIPMENT not supported. PROCESS_STEP not supported (and in any case not really supported in eT).
* For Results/Instructions blocks (maps to RequiredInputs and OptionalInputs), one or more tables with cell 0,0 beginning "Label"
   * (8/12/16) Note: For RequiredInputs:Description and OptionalInputs:Description, the character limit has been raised from 255 characters to some large (multi-kilobyte) size.
* For content aimed at the YAML Description tag, enclose in a Confluence "panel" macro.

### eT Features Not Supported and Other Stuff

* (eT) Conditional eT sequences
* (eT) A fair amount of other stuff
* (Other) High priority to add. To account for the fact that images will have to be moved to some location that the eT server is aware of, image URLs will have to be set by hand in the YAML. Plan to let the user add some URL prefix to ./config/cyml_config.py and have the script append the image filename to it in the final output.

### Known Issues
#### Issues on the input (Confluence) side

* Not really recursive, only supports a page structure with a single Confluence parent page with multiple child pages one level deep.
* Parsing of IMG tags created by the Confluence editor may be fairly wonky. 
* Cells in table heading rows - especially cell 0,0 - are important for parsing. Haven't yet reproduced, but Confluence sometimes goofs things up by changing its markup for table heading rows. If content is missing from the YAML output, check the Confluence markup (open the page in Edit mode then click the source editor control "<>" in the upper right ):

    ```html
    <!-- This markup with <thead> won't be parsed, though it occasionally appears -->
    <tbody>
    <thead>
      <th></th>
      <th></th>
    </thead>
    ...
     
    <!-- This markup with <tr> WILL be parsed -->
    <tbody>
    <tr>
      <th></th>
      <th></th>
    </tr>
    ...
    ```

#### Issues on the output (YAML) side

* YAML output contains TAB characters, which are not allowed by eT ingester. Use text editor find/replace to convert TABs to spaces.
