function rdk = RoboDK_getLink()

persistent RDK

if isempty(RDK)
    fprintf('Starting RoboDK API...\n');
    RDK = Robolink();
end
rdk = RDK;



