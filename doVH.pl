#!/usr/bin/perl

#note: this is a quick script so it's not checking file existence, etc.

#for now, set master date since I'm lazy about searching config_master
my $value = qx(grep -o 'orbits.*' configs/config_reference); 
my $reference = substr $value, 7, 8; 

print "We've set master date to $reference, change for your example\n";

print "\n\n\n\n\n\n";


#move merged slcfiles to new directory
`mv merged/SLC merged/SLC_VV`; 

#make config_master_vh, replace vv with vh, delete topo step
`cp configs/config_reference configs/config_reference_vh`;

#replace vv with vh
`sed -i 's/pol : vv/pol : vh/' configs/config_reference_vh`;

#cut off everything after "topo"
`sed -i -n '/topo/q;p' configs/config_reference_vh`;

#replace vv with vh in all pawns while renaming them at same time
#note that we've made vh version of single pol scenes, which is silly
`sed -i_vh 's/pol : vv/pol :  vh/' configs/config_secondary*`;
`sed -i 's/pol : vh/pol : vv/' configs/config_secondary*`;
`sed -i 's/pol : vv/pol : vh/' configs/config_secondary*vh`;

#make copies of resamp dir (don't have to redo range/azimuth)
`sed -i_vh '' configs/config_resamp_2*`;
#delete first function
`sed -i -e '4,14d' configs/config_resamp_2*_vh`;
#rename
`sed -i 's/Function-2/Function-1/' configs/config_resamp_2*_vh`;


#make new run_files directory 
`mkdir run_files_vh`;

#only mv required files to new run_files directory
`cp run_files/*unpack* run_files_vh`;
`cp run_files/*fullBurst_geo2rdr* run_files_vh`;
`cp run_files/*fullBurst_resample* run_files_vh`;
`cp run_files/*merge* run_files_vh`;
#but not the overlap one
# `rm run_files_vh/*overlap*`;

#replace with vh where necessary (add to end of each line)
`sed -i 's/\$/_vh/' run_files_vh/run*unpack*`;
`sed -i 's/\$/_vh/' run_files_vh/run*fullBurst_geo2rdr*`;
`sed -i 's/\$/_vh/' run_files_vh/run*fullBurst_resample*`;
#remove lat/lon/los/hgt/Mask from merge command
`sed -i -nr '/merge_[0-9]{8}/p' run_files_vh/run*merge*`;

#now sort and then remove VV-only files.
@files=split /\s+/, `ls configs/config_secondary*vh`;
foreach $file (@files){
    #does the file match SSV (i.e., is single pol)
    if(`grep SSV $file`){
        #print("$file is single-pol\n");
        $file=~/(\d{8})/;
        push @singles, $1; #this is an array with the YYYYMMDD names of single-pol
    }
}

#also add master if it's single pol
if(`grep SSV configs/config_reference_vh`){
    push @singles, $reference;
}

foreach $single (@singles){
    print("$single\n");
    `sed -i -n '/$single/!p' run_files_vh/run*`; #this command removes all lines that match that date.
}


print "now just run commands in run_files_vh\n";


