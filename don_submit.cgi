#!/usr/bin/perl
use DBI;
use CGI;
my $cgi = new CGI;
require "cgi-lib.pl";
print "Content-type:text/html; charset=UTF-8\n\n";

my $id_r = $cgi->param('id');
my $song_r = $cgi->param('song');
my $star_r = $cgi->param('star');
my $mode_r = $cgi->param('mode');
my $score_r = $cgi->param('score');
my $good_r = $cgi->param('good');
my $ok_r = $cgi->param('ok');
my $ng_r = $cgi->param('ng');
my $combo_r = $cgi->param('combo');
my $roll_r = $cgi->param('roll');
my $clear_r = $cgi->param('clear');
my ($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = localtime;
$year += 1900;
$mon += 1;
my $time_r = $year."年".$mon."月".$mday."日".$hour."時".$min."分".$sec."秒";
my @diff = ("かんたん", "ふつう", "むずかしい", "おに", "おに（裏）");

if ($good_r eq 0 && $ok_r eq 0 && $ng_r eq 0){
	$score_r = "-";
	$good_r = "-";
	$ok_r = "-";
	$ng_r = "-";
	$combo_r = "-";
	$roll_r = "-";
	$clear_r = "-";
	$time_r = "-";
}

print <<EOL;
<!DOCTYPE html>
<html>
	<head>
		<meta charset="utf-8">
		<title>スコア投稿 - 太鼓の達人 セッションでドドンがドン！</title>
		<link rel="stylesheet" href="http://hotmist.ddo.jp/~shiba560/don_score/don_score.css">
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
			<h1>スコア投稿</h1>
			<form method="post" action="don_submit.cgi"><br>
				ID：<input type="text" name="id" size="30" value="$id_r"> 　※英数字のみ
				<br><br>
				曲名：<br>
				<select name="song" size="10">
EOL

my $dbh = DBI->connect("dbi:SQLite:dbname=don_session.db");
my $sth = $dbh->prepare("select * from song order by num asc");
$sth->execute;
while(my ($num, $category, $name, $misc, $bpm, $easy_star, $norm_star, $hard_star, $extr_star, $hide_star) = $sth->fetchrow_array()){
	if($song_r eq $name){
		print "<option value=$name selected>$name</option>";
	}
	else{
		print "<option value=$name>$name</option>";
	}
}
$sth->finish;
undef $sth;
$dbh->disconnect;

print <<EOL;
				</select>
				<br><br>
				難易度：
EOL

for (my $i=0; $i<@diff; $i++){
	if($star_r eq $diff[$i]){
		print "<input type=\"radio\" name=\"star\" value=\"$diff[$i]\" checked>$diff[$i]";
		print "&nbsp;";
	}
	else{
		print "<input type=\"radio\" name=\"star\" value=\"$diff[$i]\">$diff[$i]";
		print "&nbsp;";
	}
}

print <<EOL;
				<br>
				モード：
				<input type="radio" name="mode" value="通常" checked>通常
				&nbsp;
				<input type="radio" name="mode" value="真打">真打
				<br>

				スコア：<input type="number" name="score" size="10" autocomplete="off">
				<br>
				良：<input type="number" name="good" size="10" autocomplete="off">
				<br>
				可：<input type="number" name="ok" size="10" autocomplete="off">
				<br>
				不可：<input type="number" name="ng" size="10" autocomplete="off">
				<br>

				最大コンボ：<input type="number" name="combo" size="10" autocomplete="off">
				<br>
				連打数：<input type="number" name="roll" size="10" autocomplete="off">
				<br>

				ノルマクリア：
				<input type="radio" name="clear" value="成功" checked>成功
				&nbsp;
				<input type="radio" name="clear" value="失敗">失敗

				<br><br>
				<input type="submit" value="送信">
				<p>※未入力の状態に戻したい時は良/可/不可を0としてください。</p>
			</form>
		</div>
EOL

if ($id_r ne "") {
	print "<p>以下の内容でスコアを保存しました。</p>";

	my $dbh = DBI->connect("dbi:SQLite:dbname=don_session.db");

	$dbh->{RaiseError} = 1;
	eval {

=pod
	$dbh->do("create table if not exists score(
		id nvarchar(50),
		song nvarchar(50),
		star nvarchar(10),
		mode nvarchar(10),
		score int,
		good int,
		ok int,
		ng int,
		combo int,
		roll int,
		clear nvarchar(10),
		time nvarchar(50),
		unique(id, song, star, mode));");
=cut

	$dbh->do("replace into score values
	('$id_r','$song_r','$star_r','$mode_r','$score_r','$good_r','$ok_r','$ng_r','$combo_r','$roll_r','$clear_r','$time_r');");

	my $sth = $dbh->prepare("select * from score order by id asc, song asc, star asc, mode asc;");
	$sth->execute;

	print <<EOL;
		ID：$id_r<br>
		曲名：$song_r<br>
		難易度：$star_r<br>
		モード：$mode_r<br>
		スコア：$score_r<br>
		良：$good_r<br>
		可：$ok_r<br>
		不可：$ng_r<br>
		最大コンボ：$combo_r<br>
		連打数：$roll_r<br>
		ノルマクリア：$clear_r<br>
		投稿日時：$time_r<br>
EOL

	$sth->finish;
	undef $sth;
	$dbh->disconnect;
	};
	if ($@) {
		print("Transaction aborted because $@");
	}
}

print <<EOL;
		<div class="footer">
		</div>
	</body>
</html>
EOL
