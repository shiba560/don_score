#!/usr/bin/perl

use strict;
use Encode;
use DBI;

my $dbh = DBI->connect("dbi:SQLite:dbname=don_session.db");

$dbh->do("create table song(
	num int,
	category nvarchar(50),
	name nvarchar(50),
	misc nvarchar(50),
	bpm nvarchar(20),
	easy_star int,
	norm_star int,
	hard_star int,
	extr_star int,
	hide_star int
);");

open(IN, "don_session.csv") or die;
while(my $csv = <IN>)
{
	chomp($csv);
	Encode::from_to($csv, 'Shift_JIS', 'UTF-8');
	my ($num,$category,$name,$misc,$bpm,$easy_star,$norm_star,$hard_star,$extr_star,$hide_star)
		= split(/,/, $csv);

	$dbh->do("insert into song values(
	'$num','$category','$name','$misc','$bpm','$easy_star','$norm_star','$hard_star','$extr_star','$hide_star');");
}
close(IN);

$dbh->disconnect;