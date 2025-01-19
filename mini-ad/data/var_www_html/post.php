<?php
    // ** request query format SHOULD NOT be modified **
    $method = $_SERVER['REQUEST_METHOD'];
    if (!file_exists("messages")) {
        mkdir('messages', 0777, true);
    }
    if ($method === 'POST') {
        if (isset($_GET['name'])) {
            // write mode
            $name = $_GET['name'];
            if ($name === '') {
                http_response_code(400);
                die("Missing name");
            }
            if (!isset($_GET['level']) || $_GET['level'] === '') {
                http_response_code(400);
                die("Missing level");
            }
            $level = $_GET['level'];
            if ($level == 2 || $level == 4) {
                if (file_exists('messages/' . $name)) {
                    http_response_code(409);
                    die("You Already Sent a Message");
                }
            } else if ($level == 7) {
                if (file_exists('messages/' . $name . '.png')) {
                    http_response_code(409);
                    die("You Already Sent a Message");
                }
            }
            if (!isset($_GET['message']) || $_GET['message'] === '') {
                http_response_code(400);
                die("Missing message");
            }
            $message = $_GET['message'];
            $token = random_bytes(16);
            if ($level == 2) {
                file_put_contents('messages/' . $name, $message);
            } else if ($level == 4) {
                file_put_contents('messages/' . $name, $message);
                file_put_contents('messages/' . $name . '.token', bin2hex($token));
            } else if ($level == 7) {
                $output = shell_exec('./qr-encode ' . $message);
                $lines = explode("\n", $output);
                $width = strlen($lines[0]);
                for ($i = 0; $i < $width; ++$i) {
                    if ($i == 6) continue;
                    if (ord($token[$i % 16]) & 1) {
                        $lines[$i] = substr($lines[$i], 0, 9) . ($lines[$i][9] == "0" ? "1" : "0") . substr($lines[$i], 10);
                    }
                }
                $im = @imagecreate($width + 2, $width + 2);
                $white = imagecolorallocate($im, 255, 255, 255);
                $black = imagecolorallocate($im, 0, 0, 0);
                imagefill($im, 0, 0, $white);
                for ($i = 0; $i < $width; ++$i) {
                    for ($j = 0; $j < $width; ++$j) {
                        if ( $lines[$i][$j] == "1") {
                            imagesetpixel($im, $j + 1, $i + 1, $black);
                        }
                    }
                }
                imagepng($im, 'messages/' . $name . '.png');
                imagedestroy($im);
            }
            die(bin2hex($token));
        } else {
            http_response_code(400);
            die("Missing name");
        }
    } else if ($method === 'GET') {
        if (isset($_GET['ping'])) {
            // ping request, must return "pong!" when being checked
            die("pong!");
        } else if (isset($_GET['name'])) {
            // read mode
            $name = $_GET['name'];
            if (!isset($_GET['level']) || $_GET['level'] === '') {
                http_response_code(400);
                die("Missing level");
            }
            $level = $_GET['level'];
            if ($level != 2 && !isset($_GET['token'])) {
                http_response_code(403);
                die("Forbidden");
            }
            $input_token = null;
            if ($level != 2) {
                $input_token = $_GET['token'];
                if (strlen($input_token) != 32) {
                    http_response_code(400);
                    die("Invalid Token");
                }
            }
            if ($level == 2) {
                if (file_exists('messages/' . $name)) {
                    include('messages/' . $name);
                } else {
                    http_response_code(404);
                    die("Message Not Found");
                }
            } else if ($level == 4) {
                if (file_exists('messages/' . $name)) {
                    if (file_exists('messages/' . $name . '.token')) {
                        $token = file_get_contents('messages/' . $name . '.token');
                        if ($token !== $input_token) {
                            http_response_code(403);
                            die("Forbidden");
                        }
                    }
                    include('messages/' . $name);
                } else {
                    http_response_code(404);
                    die("Message Not Found");
                }
            } else if ($level == 7) {
                /* Requirement: the return value is expected to be a pixel 1-1 QR code with dimension with border 1 no matter a token with length 32 is correct or wrong */
                header('Content-Type: image/png'); 
                $filename = 'messages/' . $name . '.png';
                $size = @getimagesize($filename);
                $im = @imagecreatefrompng($filename);
                if (!$size || !$im) {
                    die("Message Not Found");
                }
                $hex_token = hex2bin($_GET['token']);
                $white = imagecolorallocate($im, 255, 255, 255);
                $black = imagecolorallocate($im, 0, 0, 0);
                $width = $size[0];
                for ($i = 0; $i < $width - 2; ++$i) {
                    if ($i == 6) continue;
                    if (ord($hex_token[$i % 16]) & 1) {
                        $color = imagecolorat($im, 9 + 1, $i + 1);
                        imagesetpixel($im, 9 + 1, $i + 1, $color ^ 0xffffff);
                    }
                }
                imagepng($im);
                imagedestroy($im);
            }
        } else {
            // get list
            $current_time = time();
            $result = array();
            $files = scandir('messages');
            foreach ($files as $file) {
                if ($file !== '.' && $file !== '..') {
                    $time = filemtime('messages/' . $file);
                    if (($current_time - $time) > 6 * 60) { # 6 minutes
                        continue;
                    }
                    if (str_ends_with($file, '.token')) {
                        continue;
                    }
                    $level = 2;
                    $entry = array();
                    if (file_exists('messages/' . $file . '.token')) {
                        $level = 4;
                        $entry['name'] = $file;
                    } else if (str_ends_with($file, '.png')) {
                        $level = 7;
                        $entry['name'] = substr($file, 0, strlen($file) - 4);
                    } else {
                        $level = 2;
                        $entry['name'] = $file;
                    };
                    $entry['time'] = $time;
                    $entry['level'] = $level;
                    $result[] = $entry;
                }
            }
            function cmp($a, $b) {
                if ($a['time'] == $b['time']) {
                    return 0;
                }
                return ($a['time'] > $b['time']) ? -1 : 1;
            }
            usort($result, 'cmp');
            echo json_encode($result);
        }
    } else {
        http_response_code(405);
        die("Method Not Allowed");
    }
?>