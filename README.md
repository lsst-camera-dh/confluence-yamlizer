# confluence-yamlizer

### Dependencies and Installing
#### Hand-rolled libraries (in ./lib)

Please set PYTHONPATH as needed.

    * confluence/confluence_fetcher_rest
        Hard-coded Confluence login credentials in here
    * tinyxml
    * tinylogging
    * https

#### Third party libraries

    * lxml 3.3.1
    * requests 2.2.1

#### Directory structure

    The main script, confyamlizer.py, assumes ./src and ./config subdirectories.

### Page parsing requirements

* For Prerequisite table (maps to Prerequisites YAML tag), a table with cell 0,0 containing "PrerequisiteType"
**   PREPARATION prerequisite type is supported. CONSUMABLE should work. TEST_EQUIPMENT not supported. PROCESS_STEP not supported (and in any case not really supported in eT).
* For Results/Instructions and Results blocks (maps to RequiredInputs and OptionalInputs), one or more tables with cell 0,0 beginning "Label"
** (8/9/16) Note: For RequiredInputs:Description and OptionalInputs:Description, the character limit has been raised well over the original 255 characters and tested in Raw/Test. To be rolled out in Prod soon...
* For content aimed at the YAML Description tag, enclose content in a Confluence "panel" macro.

### eT Features Not Supported

    RelationshipTasks table (i.e., hardware "kitting"/assignment info)
        But seems straightforward to do
    Conditional eT sequences

### Known Issues
#### Issues on the input (Confluence) side

    * Not really recursive, only supports a page structure with a single Confluence parent page with multiple child pages one level deep.

    * Cells in table heading rows - especially cell 0,0 - are important for parsing. Haven't yet reproduced, but Confluence sometimes goofs things up by changing its markup for table heading rows. if content is missing from the YAML output, check the Confluence markup (open the page in Edit mode then click the source editor control "<>" in the upper right ) :
    <!-- This markup with <thead> won't be parsed, though it occasionally appears
    <tbody>
    <thead>
      <th></th>
      <th></th>
    </thead>
    ...
     
    <!-- This markup with <tr> WILL be parsed
    <tbody>
    <tr
      <th></th>
      <th></th>
    </tr>
    ...
    * All text in a table cell must have block-level tag (e.g. <p>) applied to it. Beware of any cell which has a mix of bare text elements enclosed by <td> plus additional <p> elements.

        For example, the following will not be parsed correctly...the two trailing <p> elements will be dropped.
        <td>
        Some bare text....
        <p>...followed by block level elements</p>
        <p>...followed by more block level elements</p>
        </td>
        The script may be updated for lxml to better parse these blocks.

#### Issues on the output (YAML) side

    * YAML output contains TAB characters, which are not allowed by eT ingester. Use text editor find/replace to convert TABs to spaces.
