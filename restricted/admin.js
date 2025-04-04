/*
    Since we're not using react, we're just going to render everything like this using 
    vanilla JS.
*/ 
var orderTableData;
function render(content)
{
    $('#view').html(content);
}

function clear()
{
    render('');
}


function updateOrder(orderID)
{
    first_name = document.getElementById("firstNameField").value;
    last_name = document.getElementById("lastNameField").value;
    cardNo = document.getElementById("cardNoField").value;
    totalCost = document.getElementById("totalCostField").value;
    date = document.getElementById("dateField").value;
    active = document.getElementById("activeField").value;

    const result = confirm("Are you sure you want to do this?");

    if(result){
        return $.ajax({
            url: '/admin/actions/updateOrder',
            data: {'orderID': orderID,
                   'firstName': first_name,
                   'lastName': last_name,
                   'cardNo': cardNo,
                   'totalCost': totalCost,
                   'date': date,
                   'active': active
            },
            type: "GET",
            success: function(result){
                destroyModal();
                renderOrdersTable();
            }
        });
        
    }
}

function updateMenu(ItemID)
{
    ItemName = document.getElementById("ItemName").value;
    ItemCost = document.getElementById("ItemCost").value;
    ItemImageURL = document.getElementById("ItemImageURL").value;

    const result = confirm("Are you sure you want to do this?");

    if(result){
        return $.ajax({
            url: '/admin/actions/updateMenu',
            data: {
                   'ItemID': ItemID,
                   'ItemName': ItemName,
                   'ItemCost': ItemCost,
                   'ItemImageURL': ItemImageURL
            },
            type: "GET",
            success: function(result){
                destroyModal();
                renderMenuTable();
            }
        });
        
    }
}

function deleteOrder(orderID)
{
    const confirmation = confirm("Are you sure that you want to delete this order?")
    
    if(confirmation)
    {
        return $.ajax({
            url: '/admin/actions/deleteOrder/'+orderID,
            type: "GET",
            success: function(result){
                renderOrdersTable();
            }
        });
    }
    
    
}

function deleteItem(itemID)
{
    const confirmation = confirm("Are you sure that you want to delete this order?")
    
    if(confirmation)
    {
        return $.ajax({
            url: '/admin/actions/deleteMenuItem/'+itemID,
            type: "GET",
            success: function(result){
                renderMenuTable();
            }
        });
    }
    
    
}

function destroyModal()
{
    const elementMBB = document.getElementById("modalBackgroundBlur");
    elementMBB.remove();
}

function createModal(orderID, receiptNo, first_name, last_name, cardNo, totalCost, date, active, status)
{
    const modalBackgroundBlur = document.createElement("div");
    modalBackgroundBlur.id="modalBackgroundBlur";
    modalBackgroundBlur.style="position: absolute; background-color: rgba(0, 0, 0, 0.48); width:100vw; height:100vh; left:0px; top: 0px;";

    document.body.appendChild(modalBackgroundBlur);
    const elementMBB = document.getElementById("modalBackgroundBlur");
    
    elementMBB.innerHTML = `
                            <center> 
                                <div id='testbox' style='position: relative; top: 100px; width:50%; background-color:white; '>
                                <table>
                                    firstName: <input type='text' style='width:50%;' value='${first_name}' id='firstNameField'/><br />
                                    lastName: <input type='text' style='width:50%;' value='${last_name}' id='lastNameField'/><br />
                                    cardNo: <input type='text' style='width:50%;' value='${cardNo}' id='cardNoField'/><br />
                                    totalCost: <input type='text' style='width:50%;' value='${totalCost}'  id='totalCostField'/><br />
                                    date: <input type='text' style='width:50%;' value='${date}' id='dateField' /><br />
                                    active: <input type='text' style='width:50%;' value='${active}' id='activeField'/><br />
                                    status: <input type='text' style='width:50%;' value='${status}' id='statusField' />

                                </table>
                                    <table>
                                        
                                        <tr>
                                            <th><a class='btn btn-primary' onclick="updateOrder('${orderID}');"> Submit </a> </th>
                                            <th><a class='btn btn-danger' onclick='destroyModal();'> Cancel </a> </th>
                                        </tr>
                                    </table>

                                </div>
                            </center>`;
}

function createMenuModal(ItemID, ItemName, ItemCost, ItemImageURL)
{
    const modalBackgroundBlur = document.createElement("div");
    modalBackgroundBlur.id="modalBackgroundBlur";
    modalBackgroundBlur.style="position: absolute; background-color: rgba(0, 0, 0, 0.48); width:100vw; height:100vh; left:0px; top: 0px;";

    document.body.appendChild(modalBackgroundBlur);
    const elementMBB = document.getElementById("modalBackgroundBlur");
    
    elementMBB.innerHTML = `
                            <center> 
                                <div id='testbox' style='position: relative; top: 100px; width:50%; background-color:white; '>
                                <table>
                                    ItemName: <input type='text' style='width:50%;' value='${ItemName}' id='ItemName'/><br />
                                    ItemCost: <input type='text' style='width:50%;' value='${ItemCost}' id='ItemCost'/><br />
                                    ItemImageURL: <input type='text' style='width:50%' value='${ItemImageURL}' id='ItemImageURL'/> <br/>
                                </table>
                                    <table>
                                        <tr>
                                            <th><a class='btn btn-primary' onclick="updateMenu('${ItemID}');"> Submit </a> </th>
                                            <th><a class='btn btn-danger' onclick='destroyModal();'> Cancel </a> </th>
                                        </tr>
                                    </table>

                                </div>
                            </center>`;
}

function getOrderData()
{
    return $.ajax({
        url: '/admin/actions/getOrders',
        type: "GET"
    });
}

function getMenuData()
{
    return $.ajax({
        url: "/admin/action/getMenuData",
        type: "GET"
    });
}
/* 
                    CREATE TABLE Item(
                    ItemID BIGINT(10),
                    ItemName VARCHAR(25),
                    ItemCost FLOAT
                   );
*/
function makeItemCard(ItemID, ItemName, ItemCost, ItemImageURL)
{
    const itemCard = `
                        <tr>
                            <td> ${ItemID} </td>
                            <td> ${ItemName} </td>
                            <td> ${ItemCost} </td>
                            <td> ${ItemImageURL} </td>
                        </tr>
                        <td> <a class='btn btn-primary' onClick="createMenuModal('${ItemID}', '${ItemName}', '${ItemCost}', '${ItemImageURL}');"> Edit </a> </td>
                        <td> <a class='btn btn-danger' onClick="deleteItem('${ItemID}');"> Delete </a> </td>
                     `;

    return itemCard;
}
function makeOrderCard(orderID, receiptNo, first_name, last_name, cardNo, totalCost, date, active, status)
{
    const orderCard = `
                        <tr>
                            <td> ${orderID} </td>
                            <td> ${receiptNo} </td>
                            <td> ${first_name} </td>
                            <td> ${last_name} </td>
                            <td> ${cardNo} </td>
                            <td> ${totalCost} </td>
                            <td> ${date} </td>
                            <td> ${active} </td>
                            <td> ${status} </td>
                        </tr>
                            <td> <a class='btn btn-primary' onClick="createModal('${orderID}', '${receiptNo}', '${first_name}', '${last_name}', '${cardNo}', '${totalCost}', '${date}', '${active}', '${status}');"> Edit </a> </td>
                            <td> <a class='btn btn-danger' onClick="deleteOrder('${orderID}');"> Delete </a> </td>
                        x
                      `;
    return orderCard;
}

async function renderMenuTable()
{
    clear();
    let menuData = await getMenuData();
    console.log(menuData);
    let items = "";

    for(let k in menuData)
    {
        d = menuData[k];
        items = items + makeItemCard(d['ItemID'], d['ItemName'], d['ItemCost'], d['ItemImageURL']);
    }

    const table = `
                    <table class='table'>
                        <tr>
                            <th> ItemID </th>
                            <th> ItemName </th>
                            <th> ItemCost </th>
                            <th> ItemImageURL </th>
                        </tr>

                        <tbody>
                            ${items}
                        </tbody>
                    </table>
                  `;
    
    render(table);
}

async function renderOrdersTable()
{
    clear();
    let orderData = await getOrderData();
    let orders = "";

    for(let k in orderData)
    {
        d = orderData[k];
        orders = orders + makeOrderCard(d['orderID'], d['receiptNo.'], d['first_name'], d['last_name'],d['card_no'],d['total_cost'], d['date'], d['active'], d['status']);
    }

    const table = `
                            <table class='table'>
                                <tr>
                                    <th> orderID </th>
                                    <th> receipt No. </th>
                                    <th> First Name </th>
                                    <th> Last Name </th>
                                    <th> Card No. </th>
                                    <th> Total Cost </th>
                                    <th> Date </th>
                                    <th> Active </th>
                                    <th> Status </th>
                                    <th> </th>
                                    <th> </th>
                                </tr>
                            
                            <tbody>
                                ${orders}
                            </tbody>
                        `;
    
    render(table);
}

function home()
{
    clear();
}