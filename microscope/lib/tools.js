isInList = function(member, list, field, compare) {
  /******************************************************************
   * Check if a given object is in the list
   * @params
   *    member - the object to compare
   *    list - the list that shoudl contain the object
   *    field - (optional) a subfield of the member and list objects
   *        on which to compare
   *    compare - (optional) comparison function to use
   *****************************************************************/
  logger.debug("Searching for " + 
      JSON.stringify(member) + " in list with contents: " + 
      JSON.stringify(list));
  var result = false;
  list.forEach(function(obj) {
    logger.trace("Checking for match with: " + JSON.stringify(obj));
    if (field) {
      if (typeof(obj[field]) === 'string' && 
          typeof(member[field]) === 'string') {
        logger.trace("comparing 2 strings");
        if (obj[field].localeCompare(member[field]) === 0) {
          result = true; 
        }
      } else {
        if (obj[field] == member[field]) {
          result = true;
        }
      }

    } else {
      if (obj == member) {
        result = true;
      }
    }
  });
  return result;
};