$(function(){
	$('button').click(function(event){
        event.preventDefault()
        
		var first_city = $('#first_city').val();
        var second_city = $('#second_city').val();
		$.ajax({
			url: '',
			data: {'first_city': first_city, 'second_city': second_city},
			type: 'POST',
			success: function(response){
                const table_data = [
                    {'Book ID': '1', 'Book Name': 'Challenging Times',
                     'Category': 'Business', 'Price': '125.60'
                    },
                    {'Book ID': '2', 'Book Name': 'Learn JavaScript',
                     'Category': 'Programming', 'Price': '56.00'
                    },
                    {'Book ID': '3', 'Book Name': 'Popular Science',
                     'Category': 'Science', 'Price': '210.40'
                    }
                  ]

                // Extract value from table header. 
                // ('Book ID', 'Book Name', 'Category' and 'Price')
                let col = [];
                for (let i = 0; i < table_data.length; i++) {
                    for (let key in table_data[i]) {
                        if (col.indexOf(key) === -1) {
                        col.push(key);
                        }
                    }
                }

                // Create table.
                const table = document.createElement("table");

                // Create table header row using the extracted headers above.
                let tr = table.insertRow(-1);                   // table row.

                for (let i = 0; i < col.length; i++) {
                let th = document.createElement("th");      // table header.
                th.innerHTML = col[i];
                tr.appendChild(th);
                }

                // add json data to the table as rows.
                for (let i = 0; i < table_data.length; i++) {

                    tr = table.insertRow(-1);

                    for (let j = 0; j < col.length; j++) {
                        let tabCell = tr.insertCell(-1);
                        tabCell.innerHTML = table_data[i][col[j]];
                    }
                }

                // Now, add the newly created table with json data, to a container.
                const divShowData = document.getElementById('showData');
                divShowData.innerHTML = "";
                divShowData.appendChild(table);
            

			},
			error: function(error){
				console.log(error);
			}
		});
	});
});

