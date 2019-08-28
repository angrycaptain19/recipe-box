var addIngredient= function() {
	var table = document.getElementById("Ingredient Table");
	var row = table.insertRow();
	var cell1 = row.insertCell(0);
	var cell2 = row.insertCell(1);
	var cell3 = row.insertCell(2);
	cell1.innerHTML = 'input placeholder="Ingredient", id="ingredientName", name="ingredientName';
	cell2.innerHTML = 'input placeholder="Amount", id="ingredientAmount", name="ingredientAmount"';
	cell3.innerHTML = 'input placeholder="Unit", id="ingredientMeasurementt", name="ingredientMeasurement"';
});		
