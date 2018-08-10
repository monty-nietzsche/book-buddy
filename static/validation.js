function validateForm() {
    var list, index, item, checkedCount,price;
    price = document.forms["form"]["price"].value;
    if (price == null || price <= 0) {
        alert("The price of package must be positive! Please check the price and try again");
        return false;
    }
    
    if (document.forms["form"]["book[]"]){

        checkedCount = 0;
        list = document.getElementsByName('book[]');
    
        for (index = 0; index < list.length; index++) {
            item = list[index];
            if (item.checked)
            {   
            checkedCount++;
            }
        }
        if  (checkedCount < 2) {
            alert ("A package must contain at least two books!");
            return false;
        } else {
            return true;
        }
    }
}