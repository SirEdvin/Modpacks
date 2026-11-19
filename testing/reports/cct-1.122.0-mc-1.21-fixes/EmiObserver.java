import java.lang.instrument.Instrumentation;
import java.nio.file.*;
import java.lang.reflect.*;
import java.util.*;
/** Read-only observer: interrogates the actual loaded EMI index in the remote client. */
public class EmiObserver {
 public static void premain(String args, Instrumentation inst) {
  Thread thread=new Thread(()->{
   for(int attempt=0;attempt<480;attempt++) {
    try {
     Thread.sleep(1000);
     Class<?> api=null,stack=null;
     for(Class<?> c:inst.getAllLoadedClasses()) {
      if(c.getName().equals("dev.emi.emi.api.EmiApi"))api=c;
      if(c.getName().equals("dev.emi.emi.api.stack.EmiStack"))stack=c;
     }
     if(api==null||stack==null)continue;
     List<?> values=(List<?>)api.getMethod("getIndexStacks").invoke(null);
     if(values.size()<100)continue;
     Method id=stack.getMethod("getId"),components=stack.getMethod("getComponentChanges"),name=stack.getMethod("getName");
     List<String> lines=new ArrayList<>();lines.add("EMI_INDEX_TOTAL\t"+values.size());
     for(Object value:new ArrayList<>(values)) {
      String key=String.valueOf(id.invoke(value));
      if(key.startsWith("computercraft:turtle_")||key.startsWith("computercraft:pocket_computer_"))
       lines.add(key+"\t"+components.invoke(value)+"\t"+name.invoke(value));
     }
     // Wait for the creative-derived upgraded variants, not merely vanilla registry items.
     if(lines.stream().noneMatch(s->s.contains("turtlematic:")||s.contains("cloudsolutions:")))continue;
     Files.write(Path.of("/root/emi-index-observation.tsv"),lines);
     return;
    }catch(Throwable error) {
     try {Files.writeString(Path.of("/root/emi-observer-error.txt"),error.toString());}catch(Exception ignored){}
    }
   }
  },"C20-read-only-EMI-observer");thread.setDaemon(true);thread.start();
 }
}
