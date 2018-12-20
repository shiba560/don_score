#!/usr/bin/perl
use DBI;
use CGI;
my $cgi = new CGI;
require "cgi-lib.pl";
print "Content-type:text/html; charset=UTF-8\n\n";

my $id_r = $cgi->param('id');
my $song_r = $cgi->param('song');
my $diff_r = $cgi->param('diff');
my $diff_star = undef;
my $allgd_color = "#FF8856"; #全良時のセル背景色
my $nong_color = "#FFFF77";  #フルコンボ時のセル背景色
my $clear_color = "#78FF94"; #ノルマクリア時のセル背景色
my @count = ("-") x 16; #($score, $good, $ok, $ng, $combo, $roll, $clear, $time)を通常/真打の２通り

print <<EOL;
<!DOCTYPE html>
<html>
	<head>
		<meta charset="utf-8">
		<title>スコア投稿 - 太鼓の達人 セッションでドドンがドン！</title>
		<link rel="stylesheet" href="http://hotmist.ddo.jp/~shiba560/don_score/don_score.css">
		<script type="text/javascript" src="http://hotmist.ddo.jp/~shiba560/javascript/jQuery/jquery-3.3.1.min.js"></script>
		<link rel="shortcut icon" href="http://hotmist.ddo.jp/~shiba560/image/donchan/favicon/don_favicon.ico" 
		type="image/vnd.microsoft.icon">
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
EOL

my $dbh = DBI->connect("dbi:SQLite:dbname=don_session.db");
$dbh->{RaiseError} = 1;
eval {
	my $sth1 = $dbh->prepare("SELECT * FROM song WHERE num=$song_r;");
	$sth1->execute;
	my ($num, $category, $name, $misc, $bpm, $easy_star, $norm_star, $hard_star, $extr_star, $hide_star) = $sth1->fetchrow_array();

	if ($diff_r eq "easy"){
		$diff_star = $easy_star;
		$diff_r = "かんたん";
	}
	elsif ($diff_r eq "norm"){
		$diff_star = $norm_star;
		$diff_r = "ふつう";
	}
	elsif ($diff_r eq "hard"){
		$diff_star = $hard_star;
		$diff_r = "むずかしい";
	}
	elsif ($diff_r eq "extr"){
		$diff_star = $extr_star;
		$diff_r = "おに";
	}
	else{
		$diff_star = $hide_star;
		$diff_r = "おに（裏）";
	}

	my $sth2 = $dbh->prepare("SELECT * FROM score WHERE id=\'$id_r\' AND song=\'$name\' AND star=\'$diff_r\';");
	$sth2->execute;

	while (my ($id, $song, $star, $mode, $score, $good, $ok, $ng, $combo, $roll, $clear, $time) = $sth2->fetchrow_array()){
		if ($mode eq "通常") {
			$count[0] = $score;
			$count[1] = $good;
			$count[2] = $ok;
			$count[3] = $ng;
			$count[4] = $combo;
			$count[5] = $roll;
			$count[6] = $clear;
			$count[7] = $time;
		}
		else {
			$count[8] = $score;
			$count[9] = $good;
			$count[10] = $ok;
			$count[11] = $ng;
			$count[12] = $combo;
			$count[13] = $roll;
			$count[14] = $clear;
			$count[15] = $time;
		}
	}

	print <<EOL;
				<p>ID：$id_r</p>
				<p>ジャンル：$category</p>
				<p>曲名：$name</p>
				<p>BPM：$bpm</p>
				<p>備考：$misc</p>

				<table id="scorechart" border="1">
					<tbody>
						<tr>
							<td width=150>$diff_r ★×$diff_star</td>
							<td width=260>通常</td>
							<td width=260>真打</td>
						</tr>
						<tr>
							<td>クリア状況</td>
EOL

	if ($count[2] eq 0 && $count[3] eq 0){
		print "<td bgcolor=\"$allgd_color\">全良</td>";
	}
	elsif ($count[3] eq 0){
		print "<td bgcolor=\"$nong_color\">フルコンボ</td>";
	}
	elsif ($count[6] eq "成功"){
		print "<td bgcolor=\"$clear_color\">ノルマクリア成功</td>";
	}
	elsif ($count[6] eq "失敗"){
		print "<td>ノルマクリア失敗</td>";
	}
	else{
		print "<td>-</td>";
	}

	if ($count[10] eq 0 && $count[11] eq 0){
		print "<td bgcolor=\"$allgd_color\">全良</td>";
	}
	elsif ($count[11] eq 0){
		print "<td bgcolor=\"$nong_color\">フルコンボ</td>";
	}
	elsif ($count[14] eq "成功"){
		print "<td bgcolor=\"$clear_color\">ノルマクリア成功</td>";
	}
	elsif ($count[14] eq "失敗"){
		print "<td>ノルマクリア失敗</td>";
	}
	else{
		print "<td>-</td>";
	}

	print <<EOL;
						</tr>
						<tr>
							<td>スコア</td>
							<td>$count[0]</td>
							<td>$count[8]</td>
						</tr>
						<tr>
							<td>良</td>
							<td>$count[1]</td>
							<td>$count[9]</td>
						</tr>
						<tr>
							<td>可</td>
							<td>$count[2]</td>
							<td>$count[10]</td>
						</tr>
						<tr>
							<td>不可</td>
							<td>$count[3]</td>
							<td>$count[11]</td>
						</tr>
						<tr>
							<td>最大コンボ</td>
							<td>$count[4]</td>
							<td>$count[12]</td>
						</tr>
						<tr>
							<td>連打数</td>
							<td>$count[5]</td>
							<td>$count[13]</td>
						</tr>
						<tr>
							<td>投稿日時</td>
							<td>$count[7]</td>
							<td>$count[15]</td>
						</tr>
					</tbody>
				</table>

			</div>
			<div class="footer">
			</div>
		</body>
	</html>
EOL

	$sth2->finish;
	undef $sth2;
	$sth1->finish;
	undef $sth1;

	$dbh->disconnect;
};
if ($@) {
	print "Transaction aborted because $@";
}