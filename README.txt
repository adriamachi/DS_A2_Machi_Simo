Explicació breu de la pràctica:

L’objectiu d’aquesta pràctica és implementar una versió distribuïda d’un algorisme per assegurar l’exclusió mútua. Per fer-ho, s’utilitzarà la tecnologia IBM-PyWren que és un projecte de codi obert que permet executar codi Python a l’escala de funcions del IBM Cloud.
Per dur a terme la pràctica, es fa servir el model de programació Map que ens proporciona el IBM-PyWren. Aquest ens permet l’execució concurrent de slaves amb la qual haurem de garantir que només un fil d’execució pugui entrar a la secció crítica de modificació del nostre fitxer result.json que estarà compartit i emmagatzemat al IBM COS. L’arquitectura d’aquest sistema es basarà en una única funció master i N funcions slave que actuaran en paral·lel demanant permís d’escriptura a la funció master. 
Més concretament, l’objectiu serà que els slaves actualitzin un únic fitxer compartit (result.json) afegint-hi el seu id corresponent sempre i quan el master hi hagi donat permís. La correctesa de la solució vindrà donada per la llista d’IDs que retornarà el master (write_permision_list) de forma local, un cop finalitzi la seva execució. Ambdues llistes, especificades anteriorment, hauran de ser iguals un cop finalitzat el codi.

	
Repositori github: 

	https://github.com/adriamachi/DS_A2_Machi_Simo