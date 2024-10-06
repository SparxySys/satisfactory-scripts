let search = "MinerMk3";
Object.keys(window.SCIM.baseLayout.saveGameParser.objects)
.filter(item => item.includes(search))
.map(item => window.SCIM.baseLayout.saveGameParser.objects[item])
.filter(obj => obj.transform)
.map(obj => ({ id: obj.pathName, location: obj.transform.translation }));
