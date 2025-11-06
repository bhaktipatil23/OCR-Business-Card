const TableHeader = () => {
  return (
    <thead>
      <tr className="bg-gradient-to-r from-navy-primary/5 to-blue-accent/5 border-b-2 border-navy-primary/10">
        <th className="text-left p-4 font-bold text-xs uppercase tracking-wider text-navy-primary">
          Sr No.
        </th>
        <th className="text-left p-4 font-bold text-xs uppercase tracking-wider text-navy-primary">
          File Name
        </th>
        <th className="text-left p-4 font-bold text-xs uppercase tracking-wider text-navy-primary">
          File Size
        </th>
        <th className="text-left p-4 font-bold text-xs uppercase tracking-wider text-navy-primary">
          File Type
        </th>
        <th className="text-left p-4 font-bold text-xs uppercase tracking-wider text-navy-primary">
          Status
        </th>
      </tr>
    </thead>
  );
};

export default TableHeader;
