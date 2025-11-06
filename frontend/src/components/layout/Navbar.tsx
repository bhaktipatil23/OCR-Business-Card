const Navbar = () => {
  return (
    <nav className="sticky top-0 z-50 bg-gradient-to-r from-navy-primary to-blue-accent border-b border-border/50 shadow-sm">
      <div className="flex items-center justify-start h-[50px] sm:h-[60px] px-3 sm:px-4">
        <div className="bg-white px-2 sm:px-3 py-1 sm:py-1.5 rounded-lg shadow-md">
          <img 
            src="/ReCircle Logo Identity_RGB-01.png" 
            alt="ReCircle Logo" 
            className="w-12 sm:w-16 h-auto object-contain"
          />
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
