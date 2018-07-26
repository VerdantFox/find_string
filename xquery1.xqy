xquery version "3.0";

(:~
: User: twilliams
: Date: 7/25/18
: Time: 2:23 PM
: To change this template use File | Settings | File Templates.
: CRAZY
:)

module namespace test_xquery1 = "test_xquery1.xqy";

(: callback for arb-get-feed - return arb paths for which user is authorized :)
declare function arb-uri-filter(
                      $schema_CRAZY as xs:string,      (: example: blah :)
                      $schema_crazy as xs:string,      (: example: blah :)
                      $param_map as map:map,    (: crazy comment :)
                      $otherthing as thing,     (: CRAZY comment :)
                      $schema_crazy as xs:string,
) as xs:string?