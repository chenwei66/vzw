<!DOCTYPE html>
<!--
To change this license header, choose License Headers in Project Properties.
To change this template file, choose Tools | Templates
and open the template in the editor.
-->
<html>
    <head>
        <meta charset="UTF-8">
        <title>Query result</title>
    </head>
    <body>
        <br><h3>Samsung Galaxy S7 Query result in JSON format </h3><br>
        <?php
        $count=$_GET["number"];
        $num=0;
        $connect = mysqli_connect("localhost", "root", "wei876", "reviewdb");
        $sql = "SELECT * FROM s_review";
        $result = mysqli_query($connect, $sql);
        $jason_array = array();
        while($row = mysqli_fetch_assoc($result)){
            $jason_array[] = $row;
            $num++;
            if($num >= $count)
                break;
        }

        echo $num; 
        echo " reviews queried";
        echo "<br><br>";
        
        echo json_encode($jason_array);
        ?>
        <br><br><br><br><br><br><br><br>
        <a href="/SamsungGalaxyS7.html">Samsung Galaxy S7 Query Page</a>
    </body>
</html>
