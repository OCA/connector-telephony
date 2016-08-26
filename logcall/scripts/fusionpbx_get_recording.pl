#!/usr/bin/perl

# Set ucp_url to something like this:
# https://webserver/cgi-bin/fusionpbx_get_recording.pl?file={odoo_uuid}&start={odoo_start}&resource={user_resource}

my(%args);
if($ENV{'REQUEST_METHOD'} eq "GET") {
   $query=$ENV{'QUERY_STRING'};
   my(@line_args)=split(/&/,$query);

   for my $arg (@line_args){
       $arg=~ s/\+/ /g; # replace + with spaces.....
       ($key,$val)=split(/=/,$arg);
       $val =~ s/%(..)/pack("c",hex($1))/ge;
       if($key eq "file" || $key eq "usename" || $key eq "content" ||$key eq "remove"  ){
	   $args{$key}=$val;
       }
   }


}
else{
    print "Content-type: text/html\n\n";
    print "No Arguments.....";
    exit 1;
}

my $time = $start;
my @months = ("Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec");
my ($sec, $min, $hour, $day,$month,$year) = (gmtime($time))[0,1,2,3,4,5];

print "Unix time ".$time." converts to ".$months[$month]." ".$day.", ".($year+1900);
print " ".$hour.":".$min.":".$sec."\n";

$resource =~ s/@/./

$filename="/usr/local/freeswitch/recordings/".$resource."/".$year."/".$months[$month]."/".$day."/".$args{"file"};
my(@stat)=stat $filename;
binmode(STDOUT);
if(open (F,"<", "$filename")){
    print "Connection: close\n";
    if($args{"content"}){
	print "Content-Type: ".$args{"content"}."\n\\";
    }
    else{
	print "Content-Type: application/octet-stream\n";
    }

    print "Content-Length: ".$stat[7]."\n";
    if($args{"usename"}){
	print "Content-Disposition: attachment; filename=\"".$args{"usename"}."\"\n\n";
    }
    else {
	print "Content-Disposition: attachment; filename=\"".$args{"file"}."\"\n\n";
    }

    while($len=sysread( F, $buf,512)){
	print $buf;
    }
    close F;
    if($args{"remove"}==1){
	unlink $filename;
    }
}
else {
    print "Connection: close\n";
    print "Content-Type: text/html\n\n";
    print "<H1>Error </H1>\n";
    print "The file ".$args{"file"}." does not exist on the server<br>\n";
    print "Please contact the administrator for more info.\n\n";
}

