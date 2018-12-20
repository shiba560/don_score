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
my @diff_j = ("かんたん", "ふつう", "むずかしい", "おに", "おに（裏）");
my @diff_e = ("easy", "norm", "hard", "extr", "hide");

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
	print <<EOL;
		<p>ID：$id_r</p>
		<p>
			（表記説明）<br>
			　難易度：かんたん/ふつう/むずかしい/おに/おに（裏）<br>
			　結果：良/可/不可　（上段）通常　（下段）真打<br>
			　セル色：緑…ノルマクリア成功　黄…フルコンボ　橙…全良
		</p>
		
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
EOL

	my $dbh = DBI->connect("dbi:SQLite:dbname=don_session.db");
	$dbh->{RaiseError} = 1;
	eval {
		my $sth1 = $dbh->prepare("SELECT num, category, name, easy_star, norm_star, hard_star, extr_star, hide_star FROM song;");
		$sth1->execute;

		while(my ($num, $category, $name, $easy_star, $norm_star, $hard_star, $extr_star, $hide_star) = $sth1->fetchrow_array()) {
			my @count = ("-") x 40; #(easy_dflt_good, easy_dflt_ok, easy_dflt_ng, easy_dflt_clear, easy_shin_good, ...)
			print <<EOL;
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
				print <<EOL;
				<form method="get" name="form1" action="don_result.cgi">
EOL
				if ($i==4 && $hide_star == "-") {
					print "<td></td>";
				}
				elsif ($count[$i*8+1] eq 0 && $count[$i*8+2] eq 0 || $count[$i*8+5] eq 0 && $count[$i*8+6] eq 0) {
					print "<td bgcolor=\"$allgd_color\"><a href=\"http://hotmist.ddo.jp/~shiba560/don_score/don_result.cgi/?id=$id_r&song=$num&diff=$diff_e[$i]\">
						$count[$i*8] / $count[$i*8+1] / $count[$i*8+2]<br>$count[$i*8+4] / $count[$i*8+5] / $count[$i*8+6]</a></td>";
				}
				elsif ($count[$i*8+2] eq 0 || $count[$i*8+6] eq 0) {
					print "<td bgcolor=\"$nong_color\"><a href=\"http://hotmist.ddo.jp/~shiba560/don_score/don_result.cgi/?id=$id_r&song=$num&diff=$diff_e[$i]\">
						$count[$i*8] / $count[$i*8+1] / $count[$i*8+2]<br>$count[$i*8+4] / $count[$i*8+5] / $count[$i*8+6]</a></td>";
				}
				elsif ($count[$i*8+3] eq "成功" || $count[$i*8+7] eq "成功") {
					print "<td bgcolor=\"$clear_color\"><a href=\"http://hotmist.ddo.jp/~shiba560/don_score/don_result.cgi/?id=$id_r&song=$num&diff=$diff_e[$i]\">
						$count[$i*8] / $count[$i*8+1] / $count[$i*8+2]<br>$count[$i*8+4] / $count[$i*8+5] / $count[$i*8+6]</a></td>";
				}
				else {
					print "<td><a href=\"http://hotmist.ddo.jp/~shiba560/don_score/don_result.cgi/?id=$id_r&song=$num&diff=$diff_e[$i]\">
						$count[$i*8] / $count[$i*8+1] / $count[$i*8+2]<br>$count[$i*8+4] / $count[$i*8+5] / $count[$i*8+6]</a></td>";
				}
				print "</form>";
			}
			print "</tr>";
		}
		$sth1->finish;
		undef $sth1;
		$dbh->disconnect;
	};

	if ($@) {
		print "Transaction aborted because $@";
	}
}

print <<EOL;
			</tbody>
		</table>
		</div>
		<div class="footer">
		</div>
	</body>
</html>
EOL
