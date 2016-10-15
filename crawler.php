<?php

if (count($argv) <= 1) {
    echo "Usage: \n\n";
    echo "php crawler.php <file with links>\n\n";
    echo "Use -h for any help!\n";
    die();
}

$links_file = $argv[1];
