xquery version "3.0";

(:~
: User: twilliams
: Date: 7/25/18
: Time: 2:28 PM
: To change this template use File | Settings | File Templates.
:)

module namespace test_xquery2 = "test_xquery2.xqy";


(: callback for arb-get-feed - return arb paths for which user is authorized :)
declare function arb-uri-filter(
                      $schema_uri as xs:string,       (: example: /case/qtest_0001 :)
                      $param_map as map:map  (: map also in-line comment :)
)example?;