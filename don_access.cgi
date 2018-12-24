#!/usr/bin/perl
use DBI;
use CGI;
my $cgi = new CGI;
require "cgi-lib.pl";
print "Content-type:text/html; charset=UTF-8\n\n";

my $id_r = $cgi->param('id');
my $allgd_color = "#FF8856"; #全良時のセル背景色
my $nong_color = "#FFFF77";  #フルコンボ時のセル背景色
my $clear_color = "#78FF94"; #ノルマクリア時のセル背景色
my $html_total = undef; #総合成績のhtml文
my $html_song = undef; #曲別成績のhtml文
my $sum = 0; #曲数合計
my $allgd_sum = 0; #全良曲数合計
my $nong_sum = 0; #フルコンボ曲数合計
my $clear_sum = 0; #ノルマクリア曲数合計
my $allgd_rate = 0; #全良率
my $nong_rate = 0; #フルコンボ率
my $clear_rate = 0; #ノルマクリア率
my @diff_j = ("かんたん", "ふつう", "むずかしい", "おに", "おに（裏）");
my @diff_e = ("easy", "norm", "hard", "extr", "hide");
my @song_count = (0) x 200; #(★×1の曲数、クリア数、フルコンボ数、全良数, ★×2の...)

print <<EOL;
<!DOCTYPE html>
<html>
	<head>
		<meta charset="utf-8">
		<title>スコア投稿 - 太鼓の達人 セッションでドドンがドン！</title>
		<link rel="stylesheet" href="http://hotmist.ddo.jp/~shiba560/don_score/don_score.css">
		<script type="text/javascript" src="http://hotmist.ddo.jp/~shiba560/javascript/jQuery/jquery-3.3.1.min.js"></script>
		<link rel="shortcut icon" href="http://hotmist.ddo.jp/~shiba560/image/donchan/favicon/don_favicon.ico" type="image/vnd.microsoft.icon">
	</head>

	<body>
		<div class="header">
			<!--<div class="header-logo">スコアボード - 太鼓の達人 セッションでドドンがドン！</div>-->
			<div class="header-list">
				<ul class="header-list">
					<li><a href="http://hotmist.ddo.jp/~shiba560/don_score/don_top.html">TOP</a></li>	
					<li><a href="http://hotmist.ddo.jp/~shiba560/don_score/don_access.cgi">ユーザー検索</a></li>
					<li><a href="http://hotmist.ddo.jp/~shiba560/don_score/don_submit.cgi">スコア投稿</a></li>
					<li><a href="http://hotmist.ddo.jp/~shiba560/don_score/don_link.html">リンク</a></li>
				</ul>
			</div>
		</div>

		<div class="main">
			<h1>ユーザー検索</h1>
			<form method="get" action="don_access.cgi" autocomplete="on"><br>
				ID：<input type="text" name="id" size="30">
				<br><br>
				<input type="submit" value="送信">
			</form>
EOL

if ($id_r ne "") {
	print "<p>ID：$id_r</p>";

	#-----曲別成績のhtml文作成-----

	$html_song = <<EOL;
		<h2>曲別成績</h2>
		<table id="scorechart" border="1">
			<thead>
				<tr>
					<th width="110">ジャンル</th>
					<th width="180">曲名</th>
					<th width="110">難易度</th>
					<th width="140">かんたん</th>
					<th width="140">ふつう</th>
					<th width="140">むずかしい</th>
					<th width="140">おに</th>
					<th width="140">おに（裏）</th>
				</tr>
			</thead>
			<tbody>
				<tr>
					<td colspan=2>（表示説明）</td>
					<td>梅/竹/松/鬼/裏</td>
					<td colspan=5>（上段）通常 （下段）真打　　　緑…ノルマクリア成功　黄…フルコンボ　橙…全良<br>
					※リンクをクリックすると詳細ページにジャンプ</td>
				</tr>
EOL

	my $dbh = DBI->connect("dbi:SQLite:dbname=don_session.db");
	$dbh->{RaiseError} = 1;
	eval {
		my $sth1 = $dbh->prepare("SELECT num, category, name, easy_star, norm_star, hard_star, extr_star, hide_star FROM song;");
		$sth1->execute;

		while(my ($num, $category, $name, $easy_star, $norm_star, $hard_star, $extr_star, $hide_star) = $sth1->fetchrow_array()) {
			my @count = ("-") x 40; #(easy_dflt_good, easy_dflt_ok, easy_dflt_ng, easy_dflt_clear, easy_shin_good, ...)
			$song_count[4*($easy_star-1)]++;
			$song_count[4*($norm_star-1) + 40]++;
			$song_count[4*($hard_star-1) + 80]++;
			$song_count[4*($extr_star-1) + 120]++;
			if($hide_star != "-"){$song_count[4*($hide_star-1) + 160]++;}

			$html_song = $html_song.<<EOL;
				<tr>
					<td>$category</td>
					<td>$name</td>
					<td>★×<br>$easy_star/$norm_star/$hard_star/$extr_star/$hide_star</td>
EOL

			my $sth2 = $dbh->prepare("SELECT id, song, star, mode, good, ok, ng, clear FROM score WHERE id==\'$id_r\' AND song==\'$name\';");
			$sth2->execute;

			while (my ($id, $song, $star, $mode, $good, $ok, $ng, $clear) = $sth2->fetchrow_array()) {
				for (my $i=0; $i<@diff_j; $i++){
					if ($star eq $diff_j[$i] && $mode eq "通常") {
						$count[$i*8] = $good;
						$count[$i*8+1] = $ok;
						$count[$i*8+2] = $ng;
						$count[$i*8+3] = $clear;
					}
					elsif ($star eq $diff_j[$i] && $mode eq "真打") {
						$count[$i*8+4] = $good;
						$count[$i*8+5] = $ok;
						$count[$i*8+6] = $ng;
						$count[$i*8+7] = $clear;
					}
				}
			}

			$sth2->finish;
			undef $sth2;

			for (my $i=0; $i<@diff_j; $i++){
				$html_song = $html_song."<form method=\"get\" name=\"form1\" action=\"don_result.cgi\">";

				if ($i==4 && $hide_star == "-") {
					$html_song = $html_song."<td></td>";
				}
				elsif ($count[$i*8+1] eq 0 && $count[$i*8+2] eq 0 || $count[$i*8+5] eq 0 && $count[$i*8+6] eq 0) {
					$html_song = $html_song.<<EOL;
					<td bgcolor=\"$allgd_color\"><a href=\"http://hotmist.ddo.jp/~shiba560/don_score/don_result.cgi/?id=$id_r&song=$num&diff=$diff_e[$i]\">
						$count[$i*8] / $count[$i*8+1] / $count[$i*8+2]<br>$count[$i*8+4] / $count[$i*8+5] / $count[$i*8+6]</a></td>
EOL
					if    ($i==0) {$song_count[4*($easy_star-1) + 3]++;}
					elsif ($i==1) {$song_count[4*($norm_star-1) + 3 + 40]++;}
					elsif ($i==2) {$song_count[4*($hard_star-1) + 3 + 80]++;}
					elsif ($i==3) {$song_count[4*($extr_star-1) + 3 + 120]++;}
					else          {$song_count[4*($hide_star-1) + 3 + 160]++;}
				}
				elsif ($count[$i*8+2] eq 0 || $count[$i*8+6] eq 0) {
					$html_song = $html_song.<<EOL;
					<td bgcolor=\"$nong_color\"><a href=\"http://hotmist.ddo.jp/~shiba560/don_score/don_result.cgi/?id=$id_r&song=$num&diff=$diff_e[$i]\">
						$count[$i*8] / $count[$i*8+1] / $count[$i*8+2]<br>$count[$i*8+4] / $count[$i*8+5] / $count[$i*8+6]</a></td>
EOL
					if    ($i==0) {$song_count[4*($easy_star-1) + 2]++;}
					elsif ($i==1) {$song_count[4*($norm_star-1) + 2 + 40]++;}
					elsif ($i==2) {$song_count[4*($hard_star-1) + 2 + 80]++;}
					elsif ($i==3) {$song_count[4*($extr_star-1) + 2 + 120]++;}
					else          {$song_count[4*($hide_star-1) + 2 + 160]++;}
				}
				elsif ($count[$i*8+3] eq "成功" || $count[$i*8+7] eq "成功") {
					$html_song = $html_song.<<EOL;
					<td bgcolor=\"$clear_color\"><a href=\"http://hotmist.ddo.jp/~shiba560/don_score/don_result.cgi/?id=$id_r&song=$num&diff=$diff_e[$i]\">
						$count[$i*8] / $count[$i*8+1] / $count[$i*8+2]<br>$count[$i*8+4] / $count[$i*8+5] / $count[$i*8+6]</a></td>
EOL
					if    ($i==0) {$song_count[4*($easy_star-1) + 1]++;}
					elsif ($i==1) {$song_count[4*($norm_star-1) + 1 + 40]++;}
					elsif ($i==2) {$song_count[4*($hard_star-1) + 1 + 80]++;}
					elsif ($i==3) {$song_count[4*($extr_star-1) + 1 + 120]++;}
					else          {$song_count[4*($hide_star-1) + 1 + 160]++;}
				}
				else {
					$html_song = $html_song.<<EOL;
					<td><a href=\"http://hotmist.ddo.jp/~shiba560/don_score/don_result.cgi/?id=$id_r&song=$num&diff=$diff_e[$i]\">
						$count[$i*8] / $count[$i*8+1] / $count[$i*8+2]<br>$count[$i*8+4] / $count[$i*8+5] / $count[$i*8+6]</a></td>
EOL
				}
				$html_song = $html_song."</form>";
			}
			$html_song = $html_song."</tr>";
		}
		$html_song = $html_song."</tbody></table>";

		$sth1->finish;
		undef $sth1;
		$dbh->disconnect;
	};

	#-----総合成績のhtml文作成-----

	$html_total = <<EOL;
		<h2>総合成績</h2>
		<table id="totalchart" border="1">
			<thead>
				<tr>
					<th width="100"></th>
					<th width="200">かんたん</th>
					<th width="200">ふつう</th>
					<th width="200">むずかしい</th>
					<th width="200">おに</th>
					<th width="200">おに（裏）</th>
				</tr>
			</thead>
			<tbody>
				<tr>
					<td>（表示説明）</td>
					<td colspan=5>ノルマクリア率 / フルコンボ率 / 全良率　（緑…ノルマクリア率100%　黄…フルコンボ率100%　橙…全良率100%）</td>
				</tr>
				<tr>
					<td>合計</td>
EOL

	for (my $i=0; $i<@diff_j; $i++){
		for (my $j=0; $j<10; $j++){
			$sum += $song_count[$j*4 + $i*40];
			$clear_sum += $song_count[$j*4 + 1 + $i*40];
			$nong_sum += $song_count[$j*4 + 2 + $i*40];
			$allgd_sum += $song_count[$j*4 + 3 + $i*40];
		}
		$nong_sum += $allgd_sum;
		$clear_sum += $nong_sum;

		$clear_rate = int($clear_sum / $sum *100);
		$nong_rate =  int($nong_sum / $sum *100);
		$allgd_rate = int($allgd_sum / $sum *100);

		if ($allgd_rate == 100){
			$html_total = $html_total."<td bgcolor=\"$allgd_color\">".$clear_rate."% / ".$nong_rate."% / ".$allgd_rate."%</td>";
		}
		elsif ($nong_rate == 100){
			$html_total = $html_total."<td bgcolor=\"$nong_color\">".$clear_rate."% / ".$nong_rate."% / ".$allgd_rate."%</td>";
		}
		elsif ($clear_rate == 100){
			$html_total = $html_total."<td bgcolor=\"$clear_color\">".$clear_rate."% / ".$nong_rate."% / ".$allgd_rate."%</td>";
		}
		else{
			$html_total = $html_total."<td>".$clear_rate."% / ".$nong_rate."% / ".$allgd_rate."%</td>";
		}

		$sum = 0;
		$clear_sum = 0;
		$nong_sum = 0;
		$allgd_sum = 0;
	}
	$html_total = $html_total."</tr>";

	for (my $i=0; $i<200/4; $i++){
		$song_count[$i*4+2] += $song_count[$i*4+3];
		$song_count[$i*4+1] += $song_count[$i*4+2];
	}

	for (my $i=1; $i<=10; $i++){
		$html_total = $html_total."<tr><td>★×$i</td>";

		for (my $j=0; $j<@diff_j; $j++){
			if ($song_count[($i-1)*4 + $j*40] != 0){
				$clear_rate = int($song_count[($i-1)*4 + 1 + $j*40] / $song_count[($i-1)*4 + $j*40] *100);
				$nong_rate =  int($song_count[($i-1)*4 + 2 + $j*40] / $song_count[($i-1)*4 + $j*40] *100);
				$allgd_rate = int($song_count[($i-1)*4 + 3 + $j*40] / $song_count[($i-1)*4 + $j*40] *100);

				if ($allgd_rate == 100){
					$html_total = $html_total."<td bgcolor=\"$allgd_color\">".$clear_rate."% / ".$nong_rate."% / ".$allgd_rate."%</td>";
				}
				elsif ($nong_rate == 100){
					$html_total = $html_total."<td bgcolor=\"$nong_color\">".$clear_rate."% / ".$nong_rate."% / ".$allgd_rate."%</td>";
				}
				elsif ($clear_rate == 100){
					$html_total = $html_total."<td bgcolor=\"$clear_color\">".$clear_rate."% / ".$nong_rate."% / ".$allgd_rate."%</td>";
				}
				else{
					$html_total = $html_total."<td>".$clear_rate."% / ".$nong_rate."% / ".$allgd_rate."%</td>";
				}
			}
			else{
				$html_total = $html_total."<td>-</td>";
			}
		}
		$html_total = $html_total."</tr>";
	}

	$html_total = $html_total."</tbody></table>";

	print "$html_total<br>$html_song";

	if ($@) {
		print "Transaction aborted because $@";
	}
}

print <<EOL;
		</div>
		<div class="footer">
		</div>
	</body>
</html>
EOL
