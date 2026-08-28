export default function GenericPage({ title }: { title: string }) {
  return (
    <div className="p-6 h-full overflow-y-auto">
      <h2 className="text-2xl font-bold mb-6 font-outfit">{title}</h2>
      <div className="glass-panel">
         <p className="text-gray-400 text-sm mb-4">This section is currently under development for the NER-LDI Command Center.</p>
         <div className="flex items-center justify-center p-12 border-2 border-dashed border-white/10 rounded-xl">
             <span className="text-gray-500 font-medium">Pending UI Implementation</span>
         </div>
      </div>
    </div>
  );
}
