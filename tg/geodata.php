<?php

function explodes($seps,$s) {
	$piece = array();
	$pieces= array($s);
	$separr = str_split($seps,1);
	print_r($separr,false);
	foreach ($separr as $sep) {
		echo($sep);
		$piece = array();
		foreach ($pieces as $p) {
			//if (strlen($p)>1) {
				$piece = array_merge($piece,explode($sep,$p));
			//}
			//elseif (strlen($p)==1) {
			//	$piece = array_push($piece,$p);
			//}
		}
		$pieces = $piece;
	}
	return $pieces;
}

function polygonCoordinates($polystr) {
	$seps = ",; 	([{)]}";
	$flat_values=explodes($seps,$polystr);
	print_r($flat_values,false);
	$values = array(array());
	$row = 0;
	while (list($k,$v) = each($flat_values)) {
		$values[$row*2]=$v; // GIS polygon vertex latitude
		if ($v=next($flat_values)) {
			$values[$row*2+1]=$v; // GIS polygon vertex longitude
		}
		$row++;
	}
	return $values;
}

print_r($a,false);
$s = "POLYGON((0 0, 10 0, 10 10, 0 10, 0 0))";
$pcs = polygonCoordinates($s);
print_r($pcs,false);


