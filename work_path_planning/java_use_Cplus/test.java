import com.sun.jna.Library;
import com.sun.jna.Native;
import com.sun.jna.Structure;

import java.awt.*;

public class test {
    // java
    public interface JnaLibrary extends Library {
        // JNA 为 dll 名称
        JnaLibrary INSTANCE = Native.load("add", JnaLibrary.class);

        Point jna_add(Point.ByValue ponit, int[] arr, int size);

        @Structure.FieldOrder({"x", "y", "z"})
        public static class Point extends Structure {

            public Point() {}
            public static class UserValue extends Point implements Structure.ByValue {

                public UserValue(float x, float y, float z) {
                    super(x, y, z);
                }
            }

            public Point(float x, float y, float z) {
                this.x = x;
                this.y = y;
                this.z = z;
            }

            public float x;
            public float y;
            public float z;
        }
    }


    public static void main(String[] args) {
        JnaLibrary.Point.UserValue startPoint = new JnaLibrary.Point.UserValue(1, 2, 3);
        int[] arr = new int[]{10,20};
        int size = 2;
        JnaLibrary.Point a = JnaLibrary.INSTANCE.jna_add(startPoint, arr, size);
        // out: 300
        System.out.println(a.x);
        System.out.println(a.y);
        System.out.println(a.z);
    }
}