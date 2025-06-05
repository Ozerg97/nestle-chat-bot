FETCH_GRAPH_QUERY = """
//////////////////////////////////////////////////////////////////////////
// 1) RECIPES
//////////////////////////////////////////////////////////////////////////
MATCH (r:Recipe)
WHERE r.vector_id IN $ids
OPTIONAL MATCH (r)-[:CONTAINS]->(ing:Ingredient)
OPTIONAL MATCH (r)-[:USES]->(p:Product)-[:BRANDED_AS]->(b:Brand)
RETURN  'Recipe'            AS type,
        r.vector_id         AS id,
        r.title             AS title,
        r.description       AS description,
        r.url               AS url,
        []                  AS nutrition_value,
        null                AS amazon_link,
        collect(DISTINCT ing.name)   AS ingredients,
        collect(DISTINCT p.title)    AS products,
        collect(DISTINCT b.name)     AS brands,
        []                           AS features,
        []                           AS stores
UNION
//////////////////////////////////////////////////////////////////////////
// 2) PRODUCTS
//////////////////////////////////////////////////////////////////////////
MATCH (p:Product)
WHERE p.vector_id IN $ids
OPTIONAL MATCH (p)-[:CONTAINS]->(ing:Ingredient)
OPTIONAL MATCH (p)-[:HAS_FEATURE]->(f:Feature)
OPTIONAL MATCH (p)-[:BRANDED_AS]->(b:Brand)
OPTIONAL MATCH (p)-[:SOLD_AT]->(s:Store)
RETURN  'Product'           AS type,
        p.vector_id         AS id,
        p.title             AS title,
        p.description       AS description,
        p.url               AS url,
        p.nutrition         AS nutrition_value,
        p.amazon_link       AS amazon_link,
        collect(DISTINCT ing.name)   AS ingredients,
        []                           AS products,
        collect(DISTINCT b.name)     AS brands,
        collect(DISTINCT f.text)     AS features,
        collect(DISTINCT {
            name: s.name,
            address: s.address,
            latitude: s.location.latitude,
            longitude: s.location.longitude
        })                          AS stores
UNION
//////////////////////////////////////////////////////////////////////////
// 3) ARTICLES
//////////////////////////////////////////////////////////////////////////
MATCH (a:Article)
WHERE a.vector_id IN $ids
RETURN  'Article'           AS type,
        a.vector_id         AS id,
        a.title             AS title,
        a.description       AS description,
        a.url               AS url,
        []                  AS nutrition_value,
        null                AS amazon_link,
        [] AS ingredients, [] AS products, [] AS brands,
        [] AS features,    [] AS stores
UNION
//////////////////////////////////////////////////////////////////////////
// 4) INFORMATIONS
//////////////////////////////////////////////////////////////////////////
MATCH (i:Information)
WHERE i.vector_id IN $ids
RETURN  'Information'       AS type,
        i.vector_id         AS id,
        i.title             AS title,
        null                AS description,
        i.url               AS url,
        []                  AS nutrition_value,
        null                AS amazon_link,
        [] AS ingredients, [] AS products, [] AS brands,
        [] AS features,    [] AS stores
UNION
//////////////////////////////////////////////////////////////////////////
// 5) BRANDS
//////////////////////////////////////////////////////////////////////////
MATCH (b:Brand)
WHERE b.vector_id IN $ids
RETURN  'Brand'             AS type,
        b.vector_id         AS id,
        b.name              AS title,
        null                AS description,
        b.url               AS url,
        []                  AS nutrition_value,
        null                AS amazon_link,
        [] AS ingredients, [] AS products, [] AS brands,
        [] AS features,    [] AS stores
"""
